import os, json

from .DocumentBase import DocumentBase

import InfoGain.Documents.DocumentOperations as DO
from .Datapoint import Datapoint

class TrainingDocument(DocumentBase):

    def __init__(self, name: str = None, content: str = "", datapoints: [Datapoint] = [], filepath: str = None):
        super().__init__(name, content, datapoints, filepath)

        self._concepts = {}

        try:
            content = json.loads(self._content)
        except:
            return 

        if "name" in content: self.name = content["name"]
        if "content" in content: self._content = content["content"]

        if "datapoints" in content:
            
            for data in content["datapoints"]:
                # Add all the datapoints to the document
                self._datapoints.append(Datapoint(data))

                # Store the text representations of the datapoints
                dom, tar = data["domain"]["concept"], data["target"]["concept"]
                if not dom in self._concepts: self._concepts[dom] = set()
                if not tar in self._concepts: self._concepts[tar] = set()

                self._concepts[dom].add(data["domain"]["text"])
                self._concepts[tar].add(data["target"]["text"])

    def concepts(self):
        return self._concepts.items()

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
            "name": self.name,
            "content": DO.cleanWhiteSpace(self._content),
            "datapoints": [point.minimise() for point in self._datapoints]
        }
        path = os.path.join(folder, filename)
        with open(path, "w") as filehandler:
            filehandler.write(json.dumps(struct, indent=4))