import os, re, logging, json
import itertools as tools

from .Ontology import Ontology

class Datapoint:

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

        self.prediction = None

        self.embedded = False
        self.lContextEmbedding, self.mContextEmbedding, self.rContextEmbedding = None, None, None

    def embedContext(self, embedder: object) -> None:
        """ Embed the context text according to the embedder function """
        self.lContextEmbedding = embedder(cleanSentence(self.lContext))
        self.mContextEmbedding = embedder(cleanSentence(self.mContext))
        self.rContextEmbedding = embedder(cleanSentence(self.rContext))
        self.embedded = True

    def features(self):
        if not self.embedded:
            raise Exception("Embeddings not set for this datapoint")

        return [self.lContextEmbedding,self.lContextEmbedding,self.lContextEmbedding], self.annotation

class Document:

    PARAGRAPH = re.compile("[\n\n]")
    SENTENCE = re.compile("(?!\w+)[.?!][^\w+]")

    def __init__(self, filepath):
        with open(filepath) as handler:
            self.content = handler.read()

    def sentences(self):
        sen = self.content.split(".")
        return [cleanSentence(s).split() for s in sen]

    @staticmethod
    def split(text: str, separator: re) -> [str]:
        """ Separate the text with the various separators that has been given. Replace all
        separators with a single separator and then split by the single separator
        
        Params:
            text - The string to be split
            separators - A list of separator strings to have the string split by
            
        Returns:
            str - A collection of ordered strings representing the initial text split by the
                separators
        """

        split = []  # The segments of the text

        while True:
            # Match the separator
            match = separator.search(text)
            if match is None: break

            # break up the text by the separator
            s, e = match.span()
            split.append(text[:s])
            text = text[e:]

        split.append(text)

        return split

class PredictionDocument(Document):
    """ Representation of processable documents. """

    def __init__(self, content=None, filepath=None):
        """ Initialise the variables """

        if content:
            self._content = content
        elif filepath:
            with open(filepath) as filehandler:
                self._content = filehandler.read()
        else:
            raise Exception("Attempted to make a document without content")

        self._datapoints = []

    def text(self) -> str:
        """ Return the document content """
        return self._content

    def datapoints(self) -> [Datapoint]:
        """ Return the datapoints within the document """
        return self._datapoints

    def processKnowledge(self, ontology: Ontology) -> None:
        """ Iterate over the document and create potential datapoints for all possible combinations 
        of the concepts that are found.
        
        Params:
            ontology - The ontology object that contains all the information about the concepts and 
                relationships we care about
        """

        self._datapoints = []  # Reset any datapoints currently stored
        reprMap = ontology.conceptText()  # Collect all the ways in which some text may mean a concept

        def createDatapoint(dom, tar, relations, sentence):
            """ Generate the datapoints and add them to the document datapoint collection """ 

            p1, p2 = (dom.span(), tar.span()) if dom.span()[0] < tar.span()[0] else (tar.span(), dom.span())

            for relation in relations:
                # Construct the datapoint
                dp = Datapoint({
                    "domain": {"concept": reprMap[dom.group(0)], "text": dom.group(0)},
                    "target": {"concept": reprMap[tar.group(0)], "text": tar.group(0)},
                    "relation": relation.name,
                    "text": sentence,
                    "context": {
                        "left": sentence[:p1[0]],
                        "middle": sentence[p1[1]:p2[0]],
                        "right": sentence[p2[1]:]
                    }
                })

                # Record the new datapoint
                self._datapoints.append(dp)

        # Split the document by the paragraph
        for paragraph in Document.split(self._content, Document.PARAGRAPH):
            for sentence in Document.split(paragraph, Document.SENTENCE):

                # Look for instances within the sentence
                instances = [match for pattern in reprMap.keys() for match in re.finditer(pattern, sentence)]

                while instances:
                    # While there are instances to work on

                    inst = instances.pop()

                    for match in instances:
                        instConcept, matchConcept = reprMap[inst.group(0)], reprMap[match.group(0)]
                        
                        relations = ontology.findRelations(domain=instConcept, target=matchConcept)
                        createDatapoint(inst, match, relations, sentence)

                        relations = ontology.findRelations(domain=matchConcept, target=instConcept)
                        createDatapoint(match, inst, relations, sentence)

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