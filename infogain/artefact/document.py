import os, uuid, json, re, itertools, logging

from ..knowledge import Ontology
from .datapoint import Datapoint

log = logging.getLogger(__name__)

class Document:  # TODO: Change the method by which concepts and relations are stored and generated
    """ A document represents a textual source, a file, paper, etc. The document provides a method
    to manipulate and extract information from the source and provides the method of processing
    the information within and ontology to generate potential datapoints within the source.

    Params:
        name (str) - The name of the document, used as the file name if saved
        content (str) - The content of the document as a string
        filepath (str) - The location of the document source, content of the location is
            made to be the content of the document
    """

    SENTENCE = re.compile(r"[^\.\?\!]\n|((\.|\?|\!)+(?=\W))")

    @classmethod
    def removeWhiteSpace(cls, raw_string: str):
        """ Remove the excessive white space within a string

        Params:
            raw_string (str) - The raw string to be cleaned

        Returns:
            str - cleaned string
        """
        if raw_string is None: return raw_string  # Return invalid raw_string
        raw_string = re.sub(r"[ \t]+", " ", raw_string)  # Minimise white space
        raw_string = re.sub(r" (?=[\.'!?,%])", "", raw_string)  # Remove whitespace before gramma
        return raw_string.strip()  # String the leading and trailing whitespace

    @classmethod
    def clean(cls, raw_string: str) -> str:
        """ Cleans a string of invalid and grammatical characters, expands words definitions,
        corrects spelling. The function cleans and returns a string

        Params:
            raw_string (str) - The raw uncleaned string

        Returns:
            cleaned (str) - The cleaned string
        """

        cleaned_string = []  # The components of the sentence
        for rawWord in raw_string.split():

            # Resolve cant
            if rawWord == "can't": rawWord = "cant"

            # Expand words
            rawWord = re.sub("n't$", " not", rawWord)

            # Remove posession
            rawWord = re.sub("'s$", "", rawWord)

            # Lower the case
            rawWord = rawWord.lower()

            # Remove dashs
            rawWord = rawWord.replace("-"," ")

            # Find words and return
            cleaned = re.findall(r"([a-z]+[-_]?[a-z]+|[a-z]+)", rawWord)

            cleaned_string += cleaned

        return " ".join(cleaned_string)

    @classmethod
    def split(cls, text: str, separators: [re]) -> [str]:
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
        splitIndexes = [match.span()[1] for separator in separators
            for match in separator.finditer(text)]
        splitIndexes = sorted(splitIndexes)

        if not splitIndexes: return [text]

        processed = [text[:splitIndexes[0]].strip()]
        processed += [text[splitIndexes[i-1]:splitIndexes[i]].strip()
            for i in range(1,len(splitIndexes))]
        processed += [text[splitIndexes[-1]:].strip()]

        return processed

    def __init__(self, name: str = None, content: str = "", filepath: str = None):

        # Save name or generate an id randomly
        self.name = name if name else uuid.uuid4().hex
        self._concepts = None
        self._relations = None

        # Save the content, overwrite provided content with read content
        self._content = content
        if filepath:
            with open(filepath) as handler:
                self._content = handler.read()

        # Clean the content of un-needed white space.
        self._content = Document.removeWhiteSpace(self._content)

        # Maintain a collection of datapoints
        self._datapoints = []

        try:
            content = json.loads(self._content)
            self.name = content.get("name", self.name)
            self._content = content.get("content", self._content)
            self._datapoints = [Datapoint(data) for data in content.get("datapoints",[])]
        except:
            pass

    def __len__(self) -> int:
        """ Return the assumed length of the document, the number of datapoints, if none give, the
        length of the content

        Returns:
            int - The length of the document. Either the size of the document of the number of data
                points
        """
        if self._datapoints: return len(self._datapoints)
        return len(self._content)

    def concepts(self) -> {str:[str]}:
        """ Return the concepts that appeared within the document's data points. Intended to
        demonstrate the text representations of the concepts within the ontology. Generate when
        asked.

        Returns:
            {str: [str]} (dict) - A mapping of concepts to aliases
        """

        # TODO: Fix this issue - If concepts is generated, further changes to this document do not change this
        if self._concepts is None:
            self._concepts = {}

            for p in self._datapoints:
                self._concepts[p.domain["concept"]] = self._concepts.get(p.domain["concept"], []) + [p.domain["text"]]
                self._concepts[p.target["concept"]] = self._concepts.get(p.target["concept"], []) + [p.target["text"]]

        return self._concepts

    def relations(self) -> {str: int}:
        """ Return a dictionary that maps relation names to an integer that represents the number of times it appears
        within the datapoints of the document.

        Returns:
            {str: int}: A dictionary mapping relation name to count of their occurance
        """

        # TODO: Changes to the document doesn't get reflexed here.
        if self._relations is None:
            self._relations = {}

            for p in self._datapoints:
                self._relations[p.relation] = self._relations.get(p.relation, 0) + 1

        return self._relations


    def text(self) -> str:
        """ Return the entire content of the document, but, doesn't construct the content from data
        points. Only provides content that was provides from source.

        Returns:
            str - A string of the contents of the document
        """
        return self._content

    def sentences(self, cleaned: bool = False) -> [str]:
        """ Breaks the contents of the source down into sentences. A toggle to clean the sentences
        as they were being returned. If the document doesn't have any source content, then the
        sentences are generated from the data points held by the document.

        Params:
            cleaned (bool) - A toggle to clean the contents

        Returns:
            sentences ([str]) - A list of strings, each string is a sentence
        """
        if self._content:
            if cleaned:
                return [Document.clean(sen)
                    for sen in Document.split(self._content, Document.SENTENCE)]
            return Document.split(self._content, Document.SENTENCE)

        if self._datapoints:
            if cleaned:
                return [Document.clean(point.text) for point in self._datapoints]
            return [point.text for point in self._datapoints]

    def words(self, cleaned: bool = False) -> [[str]]:
        """ Break down the contents of the source down into collections of words. The collections
        are of the sentences in the source. Uses the sentences function, and splits the sentences in
        place.

        Params:
            cleaned (bool) - A toggle to clean the words

        Returns:
            words ([[str]]) - A list of sentences, each sentence is a list of words
        """
        if self._content:
            if cleaned:
                return [Document.clean(sen).split()
                    for sen in Document.split(self._content, Document.SENTENCE)]
            return [sen.split() for sen in Document.split(self._content, Document.SENTENCE)]

        if self._datapoints:
            if cleaned:
                return [Document.clean(point.text).split() for point in self._datapoints]
            return [point.text for point in self._datapoints]

    def addDatapoint(self, point: Datapoint) -> None:
        """ Add a datapoint into the document. Extend the content of this document by the contents of the datapoint

        Params:
            point (Datapoint): The datapoint object to be added
        """
        self._datapoints.append(point)
        self._content += " " + point.text + "" if point.text[-1] == "." else "."

    def datapoints(self, data: [Datapoint] = None) -> [Datapoint]:
        """
        Return the datapoints held by the document. If datapoints have been provided replace
        the currently held datapoints with the new datapoins.

        Params:
            data - The collection of datapoints to introduce back into the document

        Returns:
            [Datapoint] - A structure holding the datapoints, structure depends on document type
        """
        if data:
            self._datapoints = data
            self._content = " ".join([dp.text if dp.text[-1] == "." else dp.text + "."
                for dp in self._datapoints if dp.text is not None])
        return self._datapoints

    def hasDatapoints(self) -> bool:
        """ Determine whether the the document has any datapoints """
        return len(self._datapoints) > 0


    def analyse(self, ontology: Ontology):

        self.namedEntityRecognition(ontology)
        self.coreferencing()
        self.relationExtraction(ontology)

    def namedEntityRecognition(self):
        """ Perform named entity recognition on the document, and identify a collection of entities that represent the
        ontology concepts
        """
        pass

    def coreferencing(self):
        """ Perform co-referencing on the document and identify words that have been linked with other entities that
        """
        pass

    def processKnowledge(self, ontology: Ontology) -> None:
        """ Iterate over the document and create potential datapoints for all possible combinations
        of the concepts that are found.

        Params:
            ontology - The ontology object that contains all the information about the concepts and
                relationships we care about
        """

        self._datapoints = []  # Reset the datapoints - Only want datapoints found by the ontology

        reprMap = {concept.name: {concept.name} for concept in ontology.concepts()}
        for concept in ontology.concepts():
            for alias in concept.alias:
                reprMap[alias] = reprMap.get(alias, set()).union({concept.name})

        # Compile the search patterns into a single pattern.
        patterns = [(pattern, re.compile(r"(^|(?!\s))"+pattern+r"((?=(\W(\W|$)))|(?=\s)|(?='s)|$)"))
            for pattern in reprMap.keys()]

        def createDatapoint(dom, domCon, tar, tarCon, relations, sentence):
            """ Generate the datapoints and add them to the document datapoint collection

            Params:
                dom (re.Match) - The domain match object
                domCon (Concept) - The domain concept the match represents
                tar (re.Match) - The target match object
                tarCon (Concept) - The target match object
                relations ([Relation]) - All relations that can be formed between the domain and
                    target
                sentence (str) - The sentence that this information originated from
            """

            p1, p2 = sorted((dom.span(), tar.span()))  # Sort the spans of the elements

            for relation in relations:
                # Construct the datapoint
                dp = Datapoint({
                    "domain": {"concept": domCon, "text": dom.group(0).strip()},
                    "target": {"concept": tarCon, "text": tar.group(0).strip()},
                    "relation": relation.name,
                    "text": sentence,
                    "context": {
                        "left": sentence[:p1[0]].strip(),
                        "middle": sentence[p1[1]:p2[0]].strip(),
                        "right": sentence[p2[1]:].strip()
                    }
                })
                # return the datapoints
                yield dp

        for sentence in self.sentences():

            # Look for instances within the sentence - ensuring that you only match with individual words.
            instances = []
            for rep, pattern in patterns:
                # Find the matches
                [instances.append((rep, match)) for match in list(pattern.finditer(sentence))]

            while instances:
                # While there are instances to work on
                inst_rep, inst_match = instances.pop()

                for rep, match in instances:
                    # Collect the concept names the representations relates too
                    instConcepts, matchConcepts = reprMap[inst_rep], reprMap[rep]

                    # For each combination of elements within the sentence
                    for instConcept, matchConcept in itertools.product(instConcepts, matchConcepts):

                        # Create the datapoints for the document
                        relations = ontology.findRelations(domain=instConcept, target=matchConcept)
                        [self._datapoints.append(p) for p in createDatapoint(inst_match,
                            instConcept, match, matchConcept, relations, sentence)]

                        relations = ontology.findRelations(domain=matchConcept, target=instConcept)
                        [self._datapoints.append(p) for p in createDatapoint(match,
                            matchConcept, inst_match, instConcept, relations, sentence)]

    def clone(self, *, meta_only: bool = False):
        """ Clone the document and return a new document object. if meta_only is toggles, return an document object that
        doesn't have any content, only initialised with the same meta information

        Params:
            meta_only (bool): clone this document's meta data only

        returns:
            Document:
        """

        if meta_only:
            return Document(self.name)
        else:
            cloned = Document(self.name, self._content)
            cloned.datapoints([point.clone() for point in self.datapoints()])
            return cloned

    def save(self, folder: str = "./", filename: str = None) -> None:
        """ Save the training file and it's datapoints, checks to see if the location is a file or a
        directory. If directory, the file will be saved as the name of the document currently
        set.

        Params:
            location - The location of where the training document is to be saved
        """

        path = os.path.join(folder, filename or self.name)
        with open(path, "w") as handler:
            handler.write(
                json.dumps({
                    "name": self.name,
                    "content": self._content,
                    "datapoints": [point.minimise() for point in self._datapoints]
                }),
                indent = 4
            )