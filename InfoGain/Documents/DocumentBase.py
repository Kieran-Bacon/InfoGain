
import uuid

from .Datapoint import Datapoint
from .DocumentErrors import EmptyDocument
import InfoGain.Documents.DocumentOperations as DO


class DocumentBase:
    pass

    def __init__(self, name: str = None, content: str = "", filepath: str = None):
        """
        Generate a document object that may derive from provided content or a file 
        
        Params:
            name - The name of the document, used as the file name if saved
            content - The content of the document as a string
            filepath - The location of the document source, content of the location is
                made to be the content of the document
        """

        # Save name or generate an id randomly
        self.name = name if name else uuid.uuid4().hex
        
        # Save the content, overwrite provided content with read content
        self._content = content
        if filepath:
            with open(filepath) as handler:
                self._content = handler.read()

        # Clean the content of un-needed white space.
        self._content = DO.cleanWhiteSpace(self._content)

        # Maintain a collection of datapoints
        self._datapoints = []

    def __len__(self):
        """ Return the assumed length of the document, the number of datapoints, if none give, the 
        length of the content """
        if self._datapoints: return len(self._datapoints)
        return len(self._content)
 
    def sentences(self) -> [str]:
        """ Split the content of the document into sentences, and return the collection of 
        sentences. """
        return DO.split(self._content, DO.SENTENCE)

    def datapoints(self, data: [Datapoint] = None) -> [Datapoint]:
        """
        Return the datapoints held by the document. If datapoints have been provided replace
        the currently held datapoints with the new datapoins.

        Params:
            data - The collection of datapoints to introduce back into the document

        Returns:
            [Datapoint] - A structure holding the datapoints, structure depends on document type
        """
        if data: self._datapoints = data
        return self._datapoints