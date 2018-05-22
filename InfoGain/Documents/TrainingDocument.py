import os, json

import InfoGain.Documents.DocumentOperations as DO
from .Datapoint import Datapoint


class TrainingDocument:

    def __init__(self, filename: str = None, filepath: str = None, content: dict = None):
        """ Initialise the training document

        Params:
            filepath (string) - Valid filepath to the document to be processed
            content (dict) - A collection of valid datapoints that are meant to be treated as from
                the same document
        """

        self.name = filename
        self.content = ""
        self._datapoints = []  # The datapoints extracted from the document
        self._concepts = {}  # Set of instance names of concepts within the text

        # Prefer filepath over content, open file and load data
        if not filepath is None:
            with open(filepath) as filehandler:
                content = json.load(filehandler)

        if content is None: return

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

        # Set the content
        self.content = content.get("content", " ".join([point.text for point in self.datapoints()]))
        self.content = DO.cleanWhiteSpace(self.content)

    def __len__(self):
        return len(self._datapoints)

    def sentences(self) -> [[str]]:
        """ """
        return [DO.cleanSentence(data.text).split() for data in self._datapoints]    

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

    def addDatapoint(self, point: Datapoint) -> None:
        """ Add a datapoint into the training document """
        self.content += " " + point.text
        self._datapoints.append(point)

    def removeDatapoint(self, point: Datapoint) -> None:
        del self._datapoints[self._datapoints.index(point)]

    def datapoints(self):
        for point in self._datapoints:
            yield point

    def save(self, folder: str = "./", filename: str = None) -> None:
        """
        Save the training file and it's datapoints, checks to see if the location is a file or a 
        directory. If directory, the file will be saved as the name of the document currently
        set.

        Params:
            location - The location of where the training document is to be saved
        """

        if filename is None: filename = self.name
            
        struct = {
            "name": filename,
            "content": DO.cleanWhiteSpace(self.content),
            "datapoints": [point.minimise() for point in self._datapoints]
        }
        path = os.path.join(folder, filename)
        with open(path, "w") as filehandler:
            filehandler.write(json.dumps(struct))