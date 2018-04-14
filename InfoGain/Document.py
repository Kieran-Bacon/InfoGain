import os, re, logging, json
import itertools as tools

from .Ontology import Ontology

class Document:
    pass

class PredictionDocument(Document):
    """ Representation of processable documents. """

    def __init__(self, content=None, filepath=None):

        if content:
            self.content = content
        elif filepath:
            with open(filepath) as filehandler:
                self.content = filehandler.read()
        else:
            raise Exception("Attempted to make a document without content")

        self._datapoints = []

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
                if not len(rawSentence): continue  # Empty sentence
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

    def text(self) -> str:
        """ Return the document content """
        return self.content

    def cleanText(self) -> str:
        """ Return the cleaned version of the document content """
        content = []
        for sentences in self.cleanedParagraphs:
            paragraph = []
            for sentence in sentences:
                paragraph.append(" ".join(sentence))
            content.append(" ".join(paragraph))
        return "\n".join(content)

    def processKnowledge(self, ontology: Ontology) -> None:
        """ Iterate over the document and create potential datapoints for all possible combinations 
        of the concepts that are found.
        
        Params:
            ontology - The ontology object that contains all the information about the concepts and 
                relationships we care about
        """
        reprMap = ontology.conceptText()  # Collect all the ways in which some text may mean a concept
        self._datapoints = []  # Ordered list of datapoints, as it links with location in the document

        for paragraph in self.cleanedParagraphs:
            # Iterate over every word of the document
            for sentence in paragraph:
                for position, word in enumerate(sentence):
                    if word in reprMap:
                        # Found a word that is a concept

                        for offset in range(1, ontology.contextWindow):
                            # Offset
                            if len(sentence) <= position + offset:
                                # We have finished the search for another concept to link too.
                                break

                            if sentence[position+offset] in reprMap:
                                # Found a second valid concept
                                frameStart = position - ontology.contextWindow
                                position2 = position + offset
                                word2 = sentence[position2]
                                frameEnd = position + offset + ontology.contextWindow

                                # Relation look up
                                # Test that first word is domain
                                combinations = list(tools.product(reprMap(word), reprMap(word2)))
                                for com in combinations:
                                    for relation in ontology.findRelations(domain=com[0], target=com[1]):

                                        self._datapoints.append(Datapoint({
                                            "domain": {"text": word, "concept": com[0]},
                                            "target": {"text": word2, "concept": com[1]},
                                            "relation": relation.name,
                                            "text": " ".join(sentence[frameStart: frameEnd]),
                                            "context":{
                                                "left": sentence[frameStart:position],
                                                "middle": sentence[position:position2],
                                                "right": sentence[position2:frameEnd]
                                            }
                                        }))

                                # Test that first word is target
                                combinations = list(tools.product(reprMap(word2), reprMap(word)))
                                for com in combinations:
                                    for relation in ontology.findRelations(domain=com[0], target=com[1]):

                                        self._datapoints.append(Datapoint({
                                            "domain": {"text": word2, "concept": com[0]},
                                            "target": {"text": word, "concept": com[1]},
                                            "relation": relation.name,
                                            "text": " ".join(sentence[frameStart: frameEnd]),
                                            "context":{
                                                "left": sentence[frameStart:position],
                                                "middle": sentence[position:position2],
                                                "right": sentence[position2:frameEnd]
                                            }
                                        }))

    def datapoints(self):
        """ Extract the datapoints """
        return self._datapoints


class TrainingDocument(Document):

    def __init__(self, filepath = None, content = None):
        """ Initialise the training document

        Params:
            filepath (string) - Valid filepath to the document to be processed
            content (dict) - A collection of valid datapoints that are meant to be treated as from
                the same document
        """

        self._datapoints = []  # The datapoints extracted from the document
        self._concepts = {}  # Set of instance names of concepts within the text

        # Prefer filepath over content, open file and load data
        if not filepath is None:
            with open(filepath) as filehandler:
                content = json.load(filehandler)

        for data in content["datapoints"]:

            # Process datapoint and add it to the document storage
            self._datapoints.append(Datapoint(data))

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

    def sentences(self) -> [[str]]:
        """ """
        return [cleanSentence(data.text).split() for data in self._datapoints]    

    def words(self) -> [str]:
        """ For each of the datapoints within the document, collect the datapoints text and split it
        into the words 
        
        Returns:
            [str] - An ordered list of words that appear within the document's datapoints 
        """

        #TODO: Document should contain have non datapoint words too, that should be included
        return [word for data in self._datapoints for word in data.text.split()]

    def concepts(self):
        return self._concepts.items()

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

    def embedContext(self, embedder: object) -> None:
        """ Embed the context text according to the embedder function """
        self.lContextEmbedding = embedder(cleanSentence(self.lContext))
        self.mContextEmbedding = embedder(cleanSentence(self.mContext))
        self.rContextEmbedding = embedder(cleanSentence(self.rContext))

    def __str__(self):
        return self.text

def cleanSentence(sentence: str) -> str:
    
    words = sentence.split()
    cleanedWords = []
    for word in words:
        cleaned = cleanWord(word)
        if cleaned:
            cleanedWords.append(cleaned)

    return " ".join(cleanedWords)

def cleanWord(word: str) -> str:
    """ Remove grammar and unwanted words """
    clean = re.search("\w+-\w+|\w+", word)
    if clean is None: return None
    return clean.group(0).lower()