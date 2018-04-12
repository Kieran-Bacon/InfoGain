import os, re, logging, json
import itertools as tools

from .Ontology import Ontology

class Document():
    """ Representation of processable documents. """

    def __init__(self, filepath: str):

        def cleanWord(word: str) -> str:
            """ Remove grammar and unwanted words """
            clean = re.search("([A-Z])\w+", word)
            if clean is None: raise Exception("Word couldn't be found")
            return clean.group(0)

        with open(filepath) as filehandler:
            self.content = filehandler.read()

            # Split the content into paragraphs
            rawParagraphs = self.content.split("\n\n")

            self.paragraphs, self.cleanedParagraphs = [], []
            
            # Split the paragraphs into sentences
            for rawParagraph in rawParagraphs:
                rawSentences = rawParagraph.split(".")

                sentences, cleanedSentences = [], []

                # Create a cleaned version of the sentences
                for rawSentence in rawSentences:
                    # Split the sentence into words and record the words.
                    sentence = rawSentence.split()
                    sentences.append(sentence)
                    
                    cleanedSentence = []
                    # Replace some of the pronouns with the correct concepts
                    # TODO: identify the words that that are meant to be replaced
                    for rawWord in sentence:
                        cleanedSentence.append(cleanWord(rawWord))

                    cleanedSentences.append(cleanedSentence)

                self.paragraphs.append(sentences)
                self.cleanedParagraphs.append(cleanedSentences)

    def processKnowledge(self, ontology: Ontology) -> None:
        """ Iterate over the document and create potential datapoints for all possible combinations 
        of the concepts that are found.
        
        Params:
            ontology - The ontology object that contains all the information about the concepts and 
                relationships we care about
        """

        contextWindow = 20

        reprMap = ontology.conceptText()  # Collect all the ways in which some text may mean a concept
        self._datapoints = []  # Ordered list of datapoints, as it links with location in the document

        for index, word in enumerate(self.context):
            # Iterate over every word of the document

            if word in reprMap:
                # Word is a concept

                print(word, end=" ")

                for offset in range(1, contextWindow):
                    # Scan ahead for another concept

                    if index + offset >= len(self.context): break 

                    windowStart = index - contextWindow if index - contextWindow > 0 else 0
                    index2 = index + offset
                    word2 = self.context[index2]   

                    if word2 in reprMap:
                        # Found another concept within range

                        combinations = list(tools.product(reprMap[word], reprMap[word2])) + list(tools.product(reprMap[word2], reprMap[word]))

                        for com in combinations:
                            for relation in ontology.relations():
                                if relation.hasDomain(com[0]) and relation.hasTarget(com[1]):

                                    self._datapoints.append(Datapoint({
                                        "domain": {"text": None, "concept": com[0]},
                                        "target": {"text": None, "concept": com[1]},
                                        "relation": relation.name,
                                        "text": " ".join(self.context[windowStart:index2 + contextWindow]),
                                        "context":{
                                            "left": self.context[windowStart:index],
                                            "middle": self.context[index:index2],
                                            "right": self.context[index2:index2+contextWindow]
                                        }
                                    }))

    def datapoints(self):
        if not self.datapoints:
            raise Exception("Need to process knowledge before extracting datapoints")
        return self._datapoints


class TrainingDocument(Document):

    def __init__(self, filepath = None, content = None):
        """ Initialise the training document

        Params:
            filepath (string) - Valid filepath to the document to be processed
            content (dict) - A collection of valid datapoints that are meant to be treated as from
                the same document
        """

        self._datapoints = set()  # The datapoints extracted from the document
        self._concepts = {}  # Set of instance names of concepts within the text

        # Prefer filepath over content, open file and load data
        if not filepath is None:
            with open(filepath) as filehandler:
                content = json.load(filehandler)

        for data in content["datapoints"]:

            # Process datapoint and add it to the document storage
            self._datapoints.add(Datapoint(data))

            # Extract and store the domain and the target
            if data["domain"]["concept"] in self._concepts:
                self._concepts[data["domain"]["concept"]].add(data["domain"]["text"])
            else:
                self._concepts[data["domain"]["concept"]] = {data["domain"]["text"]}

            if data["target"]["concept"] in self._concepts:
                self._concepts[data["target"]["concept"]].add(data["target"]["text"])
            else:
                self._concepts[data["target"]["concept"]] = {data["target"]["text"]}

    def __len__(self):
        return len(self._datapoints)

    def concepts(self):
        return self._concepts

    def datapoints(self):
        for point in self._datapoints:
            yield point

class Datapoint:

    def __eq__(self, other):
        if isinstance(other, Datapoint):
            # Compare the properties of the two datapoints and return if equal

            return (self.text == other.text and\
                    self.domain == other.domain and\
                    self.target == other.target and\
                    self.relation == other.relation and\
                    self.annotation == other.annotation)

        # Compare the text representation with the 
        return self.text == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.text)

    def __init__(self, data: dict):
        """ Initialise the datapoint information, unpack it from a dictionary item.

        Params:
            data - A dictionary of the datapoint information.
        """

        # TODO: include the in text value
        self.domain = data["domain"]["concept"]
        self.target = data["target"]["concept"]
        self.relation = data["relation"]

        self.text = data["text"]  # TODO: Find out what this is (not clear enough)

        self.lContext = data["context"]["left"]
        self.mContext = data["context"]["middle"]
        self.rContext = data["context"]["right"]

        self.annotation = data.get("annotation", None)

    def __str__(self):
        return self.text