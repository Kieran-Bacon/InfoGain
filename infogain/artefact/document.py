import weakref
import collections
import re
import uuid

from .entity import Entity
from .annotation import Annotation

import logging
log = logging.getLogger(__name__)

class EntitySet(collections.abc.MutableSet):
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

    def __iter__(self) -> Entity:
        if self._entities is not None: return iter(self._entities)
        else: return (entity for doc in self._owner()._sub_documents for entity in doc.entities)

    def __contains__(self, entity: Entity):
        if self._entities is not None: return entity in self._entities
        else: return any(entity in doc.entities for doc in self._owner()._sub_documents)

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
                self._indexes.insert(max(0, i-1), index)
                self._entities.insert(max(0, i-1), entity)
                break

        else:
            self._indexes.append(index)
            self._entities.append(entity)

    def index(self, entity: Entity) -> int:
        """ Return the index of an entity within the document content

        Params:
            entity (Entity): The entity to be found within the document, and whose index is to be returned

        Returns:
            int: the entities start char index within the document content
        """
        if self._entities is not None: return self._indexes[self._entities.index(entity)]
        else:
            index = 0
            for document in self._owner()._sub_documents:
                if entity in document:
                    return index + document.entities.index(entity)
                else:
                    index += len(document)

            else:
                raise ValueError("Entity does not exist within the document - {}".format(entity))

    def add(self, entity: Entity, index: int = 0) -> None:
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

    def discard(self, entity: Entity) -> bool:
        """ Remove a member entity from the entity store

        Params:
            entity (Entity): The entity to be removed

        Returns:
            bool: True if the entity was discarded
        """

        if self._entities is not None:
            if entity in self._entities:
                idx = self._entities.index(entity)
                del self._entities[idx]
                del self._indexes[idx]

                owner = self._owner()
                for ann in owner.annotations.filter(lambda ann: entity is ann.domain or entity is ann.target):
                    owner.annotations.remove(ann)

        else:
            return any(doc.entities.discard(entity) for doc in self._owner()._sub_documents)

    def filter(self, key: callable):
        """ Filter the entities within the document according to the key function given and return them in order of
        their appearance

        Params:
            key (callable e.g. f(index, entity)): A function which takes the index of the entity and the entity itself
                and returns a bool as to whether the entity is to be collected or not

        Returns:
            [Entity]: A list of entities in order of their appearance, which meant the requirements set by filter
        """
        filtered = []
        if self._entities is not None:
            # Loop over this containers entities
            for i, e in zip(self._indexes, self._entities):
                if key(i, e): filtered.append(e)

        else:
            # Loop over sub document entities
            index = 0  # Record document length for sub documents to not have to expensively work out index
            for document in self._owner()._sub_documents:
                for entity in document.entities:
                    if key(index + document.index(entity), entity): filtered.append(entity)

                index += len(document) + len(document._CONTENTJOIN)

        return filtered

    def indexes(self) -> ((int, Entity)):
        """ Generate function that yields the index-entity pairs, in respect to the documents content

        Returns:
            (int, Entity): Generator yielding index of the entity and the entity object for all entities within the
                document
        """
        if self._entities is not None:
            for ie in zip(self._indexes, self._entities):
                yield ie

        else:
            # Loop over sub document entities
            index = 0  # Record document length for sub documents to not have to expensively work out index
            for document in self._owner()._sub_documents:
                for entity in document.entities:
                    yield (index + document.entities.index(entity), entity)

                index += len(document) + len(document._CONTENTJOIN)

    def _pushTo(self, entitySet, lo: int = None, hi: int = None):
        """ Push the entities out of this set and into another (a descendant entity set) """

        if isinstance(lo, int):
            if isinstance(hi, int):
                assert lo < hi
                segment = self._owner().content[lo: hi]
                diff = (hi - lo) - len(segment.lstrip())
            else:
                segment = self._owner().content[lo:]
                diff = len(segment) - len(segment.lstrip())

        else:
            diff = 0

        for i, e in self.indexes():
            if isinstance(lo, int) and i < lo: continue
            if isinstance(hi, int) and hi < i: break
            entitySet.add(e, i - lo - diff)

    def _init(self):
        self._indexes = []
        self._entities = []

    def _clear(self):
        self._indexes = None
        self._entities = None

    def _pullFrom(self, entitySet):
        self._init()
        for i, e in entitySet.indexes():
            self.add(e, i)

class AnnotationSet(collections.abc.MutableSet):
    """ Annotation Container for a document that provides utilities for interacting with the annotations and performing
    validation steps for the document to ensure that the annotation objects are valid against the source and with
    respect to the entities they contain.

    Params:
        owner (weakref.ref): The owning document object in weak form to allow for the container to interact with the doc
    """

    def __init__(self, owner: weakref.ref):
        self._owner = owner
        self._elements = set()

    def __len__(self):
        if self._elements is not None: return len(self._elements)
        else: return sum(len(doc.annotations) for doc in self._owner()._sub_documents)

    def __iter__(self) -> Annotation:
        if self._elements is not None: return iter(self._elements)
        return (annotation for doc in self._owner()._sub_documents for annotation in doc.annotations)

    def __contains__(self, annotation: Annotation):
        if self._elements is not None: return annotation in self._elements
        else: return any(annotation in doc.annotations for doc in self._owner()._sub_documents)

    def add(self, annotation: Annotation) -> None:
        """ Add the annotation object to the document and ensure that entities of the annotation are present and a
        annotation can be formed between them

        Params:
            annotation (Annotation): The annotation object to be added
        """

        if self._elements is None:
            # Attempt to add annotation to a sub-document
            for doc in self._owner()._sub_documents:
                # Ensure that both the domain and target of the annotation is present within the document before adding
                if annotation.domain in doc.entities and annotation.target in doc.entities:
                    return doc.annotations.add(annotation)

            else:
                # Either the entities didn't exist, or they weren't in the same sub-document - can't add annotation
                raise ValueError("Invalid annotation object - could not form annotation between those entities")

        # Sort the annotation entities into their appearance order and return their index
        (i, e), (j, e2) = sorted(
            [(self._owner().entities.index(e), e) for e in [annotation.domain, annotation.target]],
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
            raise NotImplementedError("Currently don't support annotations that form across multiple sentences")

        annotation._owner = self._owner
        annotation.context = context
        self._elements.add(annotation)

    def discard(self, annotation: Annotation) -> bool:
        """ Remove an annotation from the document

        Params:
            annotation (Annotation): The annotation object to be removed

        Raises:
            KeyError: In the event that the annotation doesn't exist
        """

        if self._elements is not None:
            if annotation in self._elements:
                self._elements.remove(annotation)
                annotation._owner = None
                return True

        else:
            return any(doc.annotations.discard(annotation) for doc in self._owner()._sub_documents)


    def _findbreakpoints(self, i) -> (int, int):
        """ Find within the document places where the sentences split the text, return the encompassing break point
        indexes for the index provided

        Params:
            i (int): The index who is being encapsulated

        Returns:
            (int, int): int <= i <= int - The indexes of before and after i of break points
        """

        # Identify all the breakpoint locations
        breakpoints = [m.span()[0] for m in re.finditer(r"^|\.|$", self._owner().content)]

        # Iterate through breakpoints to find location
        previous = None
        for point in breakpoints:
            if i < point:
                return (previous, point)

            previous = point

        # Index falls outside the content of the document
        raise ValueError("Annotation entity index out of range {} - {}".format(breakpoints, i))

    def filter(self, key: callable):
        """ Filter the annotations within a document.

        Params:
            key (callable): Function that takes an annotation object and indicates if it is to be returned
        """

        if self._elements is not None:
            return [ann for ann in self._elements if key(ann)]

        else:
            return [ann for doc in self._owner()._sub_documents for ann in doc.filter(key)]

    def _pushTo(self, annotationSet):

        toRemove = set()
        entities = annotationSet._owner().entities

        for annotation in self._elements:
            if annotation.domain in entities and annotation.target in entities:
                annotationSet.add(annotation)
                toRemove.add(annotation)

            elif annotation.domain in entities or annotation.target in entities:
                # Only one of the entities are within the set: annotation is not valid anymore
                toRemove.add(annotation)

        # Reduce the relations within this set
        self._elements = self._elements.difference(toRemove)

    def _pullFrom(self, annotationSet):
        if self._elements is None: self._elements = set()
        for annotation in annotationSet: self.add(annotation)

    def _clear(self):
        """ Switch to being a pass through annotations container """
        self._elements = None

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

        # Set the initial values for the document
        self.name = name if name else uuid.uuid4().hex
        self._break = text_break
        self._content = None
        self._length = None
        self._sub_documents = []

        self._entities = EntitySet(weakref.ref(self))
        self._annotations = AnnotationSet(weakref.ref(self))

        if content is not None:
            self._content = self._processContent(content) if not processed else content.strip()
            self._length = len(self._content)
        else:
            self._entities._clear()
            self._annotations._clear()

        self._yieldedSection = None  # Record the index of the subdocument that the entity is to exist in
        self._yieldedSentence = 0  # Record the length of previous sentences within the document
        self._yieldedWord = 0  # Record previous word lengths



    def __len__(self):
        if self._content is not None: return self._length
        return sum(len(doc) for doc in self._sub_documents) + len(self._CONTENTJOIN)*(len(self._sub_documents) - 1)

    def __iter__(self) -> str:
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
    def breaktext(self) -> str: return self._break
    @property
    def entities(self) -> EntitySet: return self._entities
    @property
    def annotations(self) -> AnnotationSet: return self._annotations

    @property
    def content(self) -> str:
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
            self.annotations._pushTo(subDocument.annotations)

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
                self.annotations._pushTo(subDocument.annotations)

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
            self.annotations._pushTo(subDocument.annotations)

            # Add the final sub document section
            if key: key(subDocument)
            self._sub_documents.append(subDocument)

        # Un-assign document variables to act as container now
        self._content = None
        self._length = None
        self.entities._clear()
        self.annotations._clear()

    def join(self, joining: (str, callable)):

        # Perform no action if there is nothing to join within the document
        if self._content is not None:
            log.warning("Join called on a top level document - no action taken")

        # If the sub documents within the document have sub documents, pass on the joining to them to join their level
        elif self._sub_documents[0]._content is None:
            for document in self._sub_documents:
                document.join(joining)

        else:
            if isinstance(joining, str):
                # Convert a string joining into a basic join method
                def joiningMethod(document1, document2):

                    # Update the content of the document content
                    documentLength = len(document1) + len(joining)
                    document1._content = document1.content + joining + document2.content
                    document1._length = len(document.content)

                    # Update the entities and annotations of the document
                    for i, e in document2.entities.indexes(): document1.entities.add(e, documentLength+ i)
                    document1.annotations._pullFrom(document2.annotations)

                    return document1

            else:
                # Reassign the user defined join method
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
            self._annotations._pullFrom(document.annotations)

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
            content = re.sub(word, replacement, content, flags=re.IGNORECASE)

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