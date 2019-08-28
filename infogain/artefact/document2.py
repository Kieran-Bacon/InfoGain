import weakref
import collections
import re
import uuid

import logging
log = logging.getLogger(__name__)

class Entity:

    def __init__(self, classType: str, surfaceForm: str, confidence: float = 1.):
        self.classType = classType
        self.surfaceForm = surfaceForm
        self.confidence = confidence

class Annotation:

    def __init__(self):
        self.domain = Entity()
        self.type = "Name"
        self.target = Entity()

        self.prediction = 0.0
        self.confidence = 0.0
        self.annotation = None

class EntitySet: #(collections.abc.MutableSequence):

    def __init__(self, owner: weakref.ref):
        self._owner = owner
        self._elements = {}

    def add(self, entity: Entity, index: int = 0):

        # Get reference to the owning document
        owner = self._owner()

        # Determine the start char index of entity - this includes lengths from yields
        index += owner._yieldedSentence + owner._yieldedWord

        if not owner._sub_documents:
            # The document hasn't been split - check that its applicable and add the entity
            assert owner.content[index:index + len(entity.surfaceForm)] == entity.surfaceForm

            # Record the entity against the index
            self._elements[index] = entity

        else:

            if owner._yieldedSection:
                # The user is within a yielded section - pass to sub document to handle
                owner._sub_documents[owner._yieldedSection].entities.add(entity, index)

            else:
                # The user has added the entity at the top level for a subsection - expensive search

                searchedSpace = 0
                searchPile = iter(owner._sub_documents)

                while True:

                    # Extract a document - determine it's length
                    doc = next(searchPile)
                    docLength = len(doc.content) + len(doc.breaktext) if owner._isForward else len(doc.content)

                    if searchedSpace + docLength < index:
                        # Found document that shall contain the entity
                        return doc.entities.add(entity, index - searchedSpace)

                    # Add the document length to the searched space - ensure that the break text has been counted
                    searchedSpace += docLength if owner._isForward else docLength + len(doc.breaktext)

    def filter(self, key: callable):

        for index, entity in self._entities:
            pass
            #Allow for filtering on the index of the entity (the start char number)


        pass

    def indexes(self) -> (int, Entity):
        """ Return iterable with index of entity and entity in the content of the document """
        pass

class AnnotationSet: #(collections.abc.MutableSet):

    def __init__(self, owner: weakref.ref):
        self._owner = owner

    def filter(key: callable):
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
    _APOSTROPHES_RGX = re.compile(r"({})".format("|".join(_APOSTROPHESMAPPER.keys())))

    def __init__(self, content: str = None, *, name: str = None, text_break: str = "", processed: bool = False):

        self.name = name if name else uuid.uuid4().hex

        self._content = self._processContent(content) if not processed else content.strip()
        self._break = text_break

        self._isForward = None
        self._sub_documents = []

        self._yieldedSection = None  # Record the index of the subdocument that the entity is to exist in
        self._yieldedSentence = 0  # Record the length of previous sentences within the document
        self._yieldedWord = 0  # Record previous word lengths

        self._entities = EntitySet(weakref.ref(self))
        self._annotations = AnnotationSet(weakref.ref(self))

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
    def entities(self): return self._entities
    @property
    def annotations(self): return self._annotations

    @property
    def content(self):
        """ Get the content for the document or form the document by combinding the sub-documents """
        if self._content:
            return self._content

        else:
            # Combine the sub-documents in the direction they were broken with inserting the break-text indicator
            if self._isForward:
                return "".join([doc.breaktext + doc.content for doc in self._sub_documents])
            else:
                return "".join([doc.content + doc.breaktext for doc in self._sub_documents])

    @content.setter
    def content(self, content: str):
        self.__init__(content, name = self.name)

    def sentences(self):
        """ Generator for the content of a document, yielding each lines. The yielder records information about yielded
        lines such that entity addition and annotation addition can be in respect to the yielded information.
        """

        for section in self:
            self._yieldedSentence = 0

            # A new section (document) shall reset the yieldedSentence value
            for match in self._SENTENCE_RGX.finditer(section):

                start, end = match.span()
                sentence = section[self._yieldedSentence: start]

                print("Sentence:", sentence, bool(sentence))
                if sentence: yield sentence

                self._yieldedSentence = end

            finalSentence = section[self._yieldedSentence:]
            if finalSentence:
                yield finalSentence

        self._yieldedSentence = 0

    def words(self):
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

            subDocument = Document(self._content, name=self.name, processed=True)
            # for i, e in self.entities.indexes(): sub_document.entities.add(e, i)
            # for annotation in self.annotations: sub_document.annotations.add(annotation)

            key(subDocument)
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

            # Add the final sub document section
            if key: key(subDocument)
            self._sub_documents.append(subDocument)

        # Un-assign document variables to act as container now
        self._content = None

    def join(self, joining: (str, callable), forward= True, callback=callable ):
        # Join the bottom level of splits by some value, which can be callable for the first or second text block
        # to determine how its to be joined
        # Callback at the end to work on the completed joined sections.
        pass


    def clone(self):
        pass

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
