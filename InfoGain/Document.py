import logging, json

from .Ontology import Ontology

class Document():
    """ Representation of processable documents. """

    def __init__(self):
        pass

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

        self.annotation = data["annotation"]