import weakref
import collections
import re
import uuid

from .entity import Entity
from .annotation import Annotation

import logging
log = logging.getLogger(__name__)


class EntitySet:
    """ An entity container for a document, keeping entities and linking them to the surfact forms within the documents
    content. For nested documents, the container acts as a pass through to child elements

    Params:
        owner (weakref.ref): A weak reference back to the owning document
    """

    def __init__(self, owner: weakref.ref):
        self._owner = owner

        # Hold the character indexes of the respective entity elements
        self._indexes = []
        self._entities = []

    def __len__(self):
        if self._entities is not None: return len(self._entities)
        else: return sum(len(doc.entities) for doc in self._owner()._sub_documents)

    def __iter__(self):
        if self._entities is not None:
            return iter(self._entities)
        else:
            return (entity for doc in self._owner()._sub_documents for entity in doc.entities)

    def __contains__(self, entity: Entity):
        if self._entities: return entity in self._entities

    def _insert(self, index: int, entity: Entity):
        """ Record the entity at the given location, insert the index and the entity into the two internal stores and
        keep consistency. Can (should) only be called on a bottom level entities container.

        Params:
            index (int): The index of the starting character of the entity in the owning document content
            entity (Entity): The entity that is found at that location

        Raises:
            RuntimeError: In the event that the container is not bottom level
        """
        if self._indexes is None or self._entities is None:
            raise RuntimeError("Calling _insert on non-bottom level entity container")

        for i, idx in enumerate(self._indexes):
            if index < idx:
                self._indexes.insert(index, max(0, i-1))
                self._entities.insert(entity, max(0, i-1))
                break

        else:
            self._indexes.append(index)
            self._entities.append(entity)

    def index(self, entity: Entity) -> int:
        #TODO: Make this work for non bottom level containers
        return self._indexes[self._entities.index(entity)]

    def add(self, entity: Entity, index: int = 0):
        """ Add an entity into the entity container at the given index. Ensure that the entity is valid for the proposed
        location and take advantage of the yielded context to be able to provided a relative index rather than a global
        context.

        If adding an entity within the iter, sentence, word scope of the document, provide an index that is relative to
        that block

        Params:
            entity (Entity): The entity to be added
            index (int): The start char within the document content (or section/sentence/word content)

        Raises:
            ValueError: The location's surfaceForm doesn't agree with the entities
            ValueError: The index is out of bounds for the document
            RuntimeError: Though the index was valid, a section couldn't be found that contains it
        """

        # Get reference to the owning document
        owner = self._owner()

        # Determine the start char index of entity - this includes lengths from yields
        index += owner._yieldedSentence + owner._yieldedWord

        if not owner._sub_documents:
            # The document hasn't been split - check that its applicable and add the entity
            if not owner.content[index:index + len(entity.surfaceForm)] == entity.surfaceForm:
                raise ValueError("Entity couldn't be found (\"{}'{}'{}\") != '{}'".format(
                        owner.content[max(0, index - 10): index],
                        owner.content[index:index + len(entity.surfaceForm)],
                        owner.content[index + len(entity.surfaceForm): index + len(entity.surfaceForm) + 10],
                        entity.surfaceForm
                    )
                )

            # Record the entity against the index
            self._insert(index, entity)

        else:

            if owner._yieldedSection:
                # The user is within a yielded section - pass to sub document to handle
                owner._sub_documents[owner._yieldedSection].entities.add(entity, index)

            else:
                # The user has added the entity at the top level for a subsection

                # Ensure valid add
                if index >= len(owner): raise ValueError("Entity index out of range - length {}".format(len(owner)))

                # Set up search variables
                searchedSpace = 0
                searchPile = iter(owner._sub_documents)
                separatorLength = len(owner._CONTENTJOIN)

                for doc in searchPile:
                    # Find the length of the sub document
                    docLength = len(doc) if not searchPile else len(doc) + separatorLength

                    if searchedSpace + docLength > index:
                        # Found document that shall contain the entity
                        return doc.entities.add(entity, index - searchedSpace)

                    # Add the document length to the searched space - ensure that the break text has been counted
                    searchedSpace += docLength

                else:
                    raise RuntimeError("index out of range")

    def filter(self, key: callable):
        #TODO MAKE THIS WORK FOR SPLIT DOCUMENTS
        filtered = []
        for i, e in  zip(self._indexes, self._entities):
            if key(i, e): filtered.append(e)

        return e

    def indexes(self):
        for ie in zip(self._indexes, self._entities):
            yield ie

    def _pushTo(self, entitySet, lo: int = None, hi: int = None):
        """ Push the entities out of this set and into another (a descendant entity set) """

        # Calculate the difference in the segment for the entity set given that white space is stripped out
        if isinstance(lo, int) and isinstance(hi, int):
            assert lo < hi
            segment = self._owner().content[lo: hi]
            diff = (hi - lo) - len(segment.lstrip())

        elif isinstance(lo, int):
            diff = lo - len(self._owner().content[lo:].lstrip())

        else:
            diff = 0

        for i, e in self.indexes():
            if isinstance(lo, int) and i < lo: continue
            if isinstance(hi, int) and hi < i: break
            entitySet.add(e, i - lo - diff)

    def _clear(self):
        self._indexes = None
        self._entities = None

    def _pullFrom(self, entitySet):

        if self._indexes is None:
            self._indexes = []
            self._entities = []

        for i, e in entitySet.indexes():
            self.add(e, i)

class AnnotationSet: #(collections.abc.MutableSet):

    def __init__(self, owner: weakref.ref):
        self._owner = owner

        self._breakpoints = [m.span()[0] for m in re.finditer(r"[^\.$]", self._owner().content)]

    def add(self, annotation: Annotation):

        # Sort the annotation entities into their appearance order and return their index
        i, e, j, e2 = sorted(
            [(self._owner.entities.index(e), e) for e in [annotation.domain, annotation.target]],
            key = lambda x: x[0]
        )

        # Find the sentence breakpoints for the entities in the annotations
        start = self._findbreakpoints(i)
        end = self._findbreakpoints(j)

        if start == end:
            # The annotation is within the same sentence
            context = (
                (start[0], i),
                (i + len(e.surfaceForm), j),
                (j + len(e2.surfaceForm), start[1])
            )

        else:
            # TODO: Consider co-referencing
            raise NotImplementedError("Currently don't support annotations that form across multiple sentences")

        annotation._owner = self
        annotation.context = context

    def _findbreakpoints(self, i):

        previous = None
        for point in self._breakpoints:
            if i < point:
                return (previous, i)

            previous = point

        raise ValueError("Annotation entity index out of range {} - {}".format(self._breakpoints, i))

    def filter(self, key: callable):
        pass

class Document:
    """ A document represents a textual source, a file, paper, etc. The document provides a method
    to manipulate and extract information from the source and provides the method of processing
    the information within and ontology to generate potential datapoints within the source.

    Params:
        content (str) - The content of the document as a string
        *,
        name (str) - The name of the document, used as the file name if saved
        text_break (str) - The string that broke the content from another document's content
        processed (bool) - Indicate that the current content has already been processed - don't process again
    """

    _CONTENTJOIN = '. '

    _SENTENCE_RGX = re.compile(r"[^\.\?\!]\n|((\.|\?|\!)+\s*)|$")
    _WHITESPACE_RGX = re.compile(r"[ \t]+")  # Match sections of multiple while space characters
    _WHITESPACEGRAMMER_RGX = re.compile(" [,]")  # Match whitespace that proceeds a grammar item TODO
    _NOTS_RGX = re.compile(r"n't")
    _ENDINGOWNER_RGX = re.compile("'s")
    _WORDS = re.compile(r"([A-Za-z]+[-_]?[A-Za-z]+|[A-Za-z]+)")

    _APOSTROPHESMAPPER = {
        "doesn't": "does not",
        "can't": "can not",
        "won't": "will not",
        "don't": "do not",
        "i've": "i have",
        "i'd": "i would",
        "i'm": "i am",
        "i'll": "i will",
        "she's": "she is",
        "he's": "he is",
        "it's": "it is",
        "there's": "there is",
        "they're": "they are",
        "we're": "we are",
        "you've": "you have",
        "you're": "you are",
        "couldn't": "could not",
        "shouldn't": "should not",
        "wouldn't": "would not"
    }

    def __init__(self, content: str = None, *, name: str = None, text_break: str = "", processed: bool = False):

        self.name = name if name else uuid.uuid4().hex

        self._content = self._processContent(content) if not processed else content.strip()
        self._length = len(self._content)
        self._break = text_break

        self._sub_documents = []

        self._yieldedSection = None  # Record the index of the subdocument that the entity is to exist in
        self._yieldedSentence = 0  # Record the length of previous sentences within the document
        self._yieldedWord = 0  # Record previous word lengths

        self._entities = EntitySet(weakref.ref(self))
        self._annotations = AnnotationSet(weakref.ref(self))

    def __len__(self):
        if self._content is not None: return self._length
        return sum(len(doc) for doc in self._sub_documents) + len(self._CONTENTJOIN)*(len(self._sub_documents) - 1)

    def __iter__(self):
        # Iterate over the paragraphs that the document has been broken into and return their text

        if self._content:
            yield self.content
        else:

            for i, document in enumerate(self._sub_documents):
                self._yieldedSection = i  # Record the document index that is being yielded

                for paragraph in document:  # Document shall record it's own section yielded
                    yield paragraph

            self._yieldedSection = None

    @property
    def breaktext(self): return self._break
    @property
    def entities(self) -> EntitySet: return self._entities
    @property
    def annotations(self) -> AnnotationSet: return self._annotations

    @property
    def content(self):
        """ Get the content for the document or form the document by combinding the sub-documents """
        if self._content:
            return self._content

        else:
            # Combine the sub-documents in the direction they were broken with inserting the break-text indicator
            return self._CONTENTJOIN.join([doc.content for doc in self._sub_documents])

    @content.setter
    def content(self, content: str):
        self.__init__(content, name = self.name)

    def sentences(self) -> str:
        """ Generator for the content of a document, yielding each lines. The yielder records information about yielded
        lines such that entity addition and annotation addition can be in respect to the yielded information.
        """

        for section in self:
            self._yieldedSentence = 0

            # A new section (document) shall reset the yieldedSentence value
            for match in self._SENTENCE_RGX.finditer(section):

                start, end = match.span()
                sentence = section[self._yieldedSentence: start]

                if sentence: yield sentence

                self._yieldedSentence = end

            finalSentence = section[self._yieldedSentence:]
            if finalSentence:
                yield finalSentence

        self._yieldedSentence = 0

    def words(self) -> str:
        """ Return all the words of the document ensuring that they are valid. Words that contain non alphabetical
        characters shall not be yielded from this function
        """

        for sentence in self.sentences():
            self._yieldedWord = 0

            for match in self._WHITESPACE_RGX.finditer(sentence):
                yield sentence[self._yieldedWord: match.span()[0]]
                self._yieldedWord = match.span()[1]

            yield sentence[self._yieldedWord:]

        self._yieldedWord = 0

    def split(self, break_indicator: str, *, key: callable = None, forward: bool = True) -> None:
        """ Split the text such that there are different sections for the text, such that entities and annotations are
        kept separate and are edittable on mass. Provide functions to run at the point of break

        Params:
            break_indicator (str): The break text used to split the content of the document
            *,
            key (callable): function/lambda to work break indicator the entities/annotations of each section
            forward (bool): toggle the direction of the break
        """

        if not self._content:
            # Pass the break text indicator down to sub documents
            for document in self._sub_documents:
                document.split(break_indicator, key=key, forward=forward)
            return

        breakPoints = list(re.finditer(break_indicator, self._content))
        if not breakPoints:
            # The document doesn't contain any break points - as other documents might - descend current document
            log.warning("document {} could not be split by break-indicator {}".format(self.name, break_indicator))

            # Create a new sub document - the only at the new level (to be consistent with documents of this level)
            subDocument = Document(self._content, name=self.name, processed=True)
            self.entities._pushTo(subDocument.entities)
            # for annotation in self.annotations: sub_document.annotations.add(annotation)

            # Run the split function on the document and
            if key: key(subDocument)
            self._sub_documents.append(subDocument)

        else:

            previousIndex = 0
            previousBreakString = ""

            for point in breakPoints:

                # Extract the span of the break text indicator - extracting the breakstring
                start, end = point.span()
                breakString = self._content[start: end]

                # If the first section is empty continue to the next
                if previousIndex == 0 and previousIndex == start:
                    # Update iteration variables
                    previousIndex = end
                    previousBreakString = breakString
                    continue

                # Extract the snippet of the document
                subContent = self._content[previousIndex: start]

                if forward:
                    # The break indicator leads the section
                    subDocument = Document(content=subContent, text_break=previousBreakString, processed=True)

                else:
                    # The break indicator follows the section
                    subDocument = Document(content=subContent, text_break=breakString, processed=True)

                # Extract the entities for that sub-document
                self.entities._pushTo(subDocument.entities, previousIndex, start)

                # Update iteration variables
                previousIndex = end
                previousBreakString = breakString

                # Append the generated sub document
                if key: key(subDocument)
                self._sub_documents.append(subDocument)

            # Process the final snippet of text that follows the last break indicator
            subContent = self._content[end:]

            # Set up the document for the final section
            if forward:     subDocument = Document(content=subContent, text_break=breakString, processed=True)
            else:           subDocument = Document(content=subContent, processed=True)

            # Extract the entities for that sub-document
            self.entities._pushTo(subDocument.entities, end)

            # Add the final sub document section
            if key: key(subDocument)
            self._sub_documents.append(subDocument)

        # Un-assign document variables to act as container now
        self._content = None
        self._length = None
        self.entities._clear()

    def join(self, joining: (str, callable)):

        # Perform no action if there is nothing to join within the document
        if self._content is not None:
            log.warning("Join called on a top level document - no action taken")

        # If the sub documents within the document have sub documents, pass on the joining to them to join their level
        elif self._sub_documents[0]._content is None:
            for document in self._sub_documents:
                document.join(joining)

        else:

            # Convert a string joining into a basic join method
            if isinstance(joining, str):
                def joiningMethod(document1, document2):

                    documentLength = len(document1) + len(joining)
                    document1._content = document1.content + joining + document2.content
                    document1._length = len(document.content)

                    for i, e in document2.entities.indexes():
                        document1.entities.add(e, documentLength+ i)

                    return document1

            else:
                joiningMethod = joining

            # Join the documents below - extract the first document and prepare queue of remaining sub documents
            document = self._sub_documents[0]
            documents = self._sub_documents[1:]

            # Loop over the sub-documents and join their contents
            while documents:
                nextDocument = documents.pop(0)
                document = joiningMethod(document, nextDocument)

            # Update the documents internal state
            self._sub_documents = None

            self._content = document.content
            self._length = len(document.content)

            self._entities._pullFrom(document.entities)

    def clone(self, *, meta_only: bool = False):

        if meta_only:
            return Document("", name=self.name, text_break=self.breaktext)
        else:
            if self._content:
                return Document(self._content, name=self.name, text_break=self.breaktext, processed=True)
            else:
                document = Document("", name=self.name, text_break=self.breaktext, processed=True)
                document._content = None
                document._sub_documents = [document.clone() for document in self._sub_documents]
                return document

    def _processContent(self, content):

        # Remove all unwanted characters
        content = re.sub(r"[^A-Za-z0-9,\.:;'\"&£$%!?\-#@\n ]", "", content)

        # Replace all ending - any arbitrary length of ending sentence characters are collapsed
        content = re.sub(r"[\.!?]+", ".", content)

        # Replace non list : with ;
        content = re.sub(r":(?= )(?!.*;.*\.)", ";", content)

        # Replace & with and
        content = re.sub(r"&", " and ", content)

        # Reduce white space usage
        content = self._WHITESPACE_RGX.sub(" ", content)

        # Replace all apostophe's in the document:
        for word, replacement in self._APOSTROPHESMAPPER.items():
            content = re.sub(word, replacement, content) # TODO make case insensitive.

        return content.strip()

    @staticmethod
    def _split(text: str, separators: [re]) -> [str]:
        """ Separate the text with the separators that has been given. Replace all
        separators with a single separator and then split by the single separator

        Params:
            text - The string to be split
            separators - A list of separator strings to have the string split by

        Returns:
            str - A collection of ordered strings representing the initial text split by the
                separators
        """

        if not isinstance(separators, list): separators = [separators]

        # Find all the places the text needs to be split
        splitIndexes = [match.span()[1] for separator in separators for match in separator.finditer(text)]
        splitIndexes = sorted(splitIndexes)

        if not splitIndexes: return [text]

        processed = [text[:splitIndexes[0]].strip()]
        processed += [text[splitIndexes[i-1]:splitIndexes[i]].strip() for i in range(1,len(splitIndexes))]
        processed += [text[splitIndexes[-1]:].strip()]

        return processed
