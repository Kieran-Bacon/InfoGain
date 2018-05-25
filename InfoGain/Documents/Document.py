import os, re, logging, json, logging
import itertools as tools

from InfoGain.Ontology import Ontology
from .Datapoint import Datapoint

from .DocumentBase import DocumentBase
import InfoGain.Documents.DocumentOperations as DO
from InfoGain.Documents.DocumentErrors import EmptyDocument

class Document(DocumentBase):
    """ Representation of processable documents. """

    @classmethod
    def anaphoraResolution(cls, content: str) -> str:
        """ Resolve anaphorical issues present within the document """
        logging.warning("Anaphora resolution is not implemented")
        return content

    def __init__(self, name: str = None, content: dict = None, filepath: str = None,):
        super().__init__(name, content, filepath)

        try:
            content = json.loads(self._content)
        except:
            return 

        if "name" in content: self.name = content["name"]
        if "content" in content: self._content = content["content"]

        if "datapoints" in content:
            for group in content["datapoints"]:
                datapoints = []
                for data in group:
                    datapoints.append(Datapoint(data))
                self._datapoints.append(datapoints)

        #self._content = Document.anaphoraResolution(self._content)

    def processKnowledge(self, ontology: Ontology) -> None:
        """ Iterate over the document and create potential datapoints for all possible combinations 
        of the concepts that are found.
        
        Params:
            ontology - The ontology object that contains all the information about the concepts and 
                relationships we care about
        """
        if self._datapoints:
            logging.info("Avoiding processing document, datapoints already initialised")
            return 
            
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
                        "left": sentence[:p1[0]].strip(),
                        "middle": sentence[p1[1]:p2[0]].strip(),
                        "right": sentence[p2[1]:].strip()
                    }
                })

                # return the datapoints
                yield dp

        # Split the document by the paragraph
        for paragraph in DO.split(self._content, DO.PARAGRAPH):
            for sentence in DO.split(paragraph, DO.SENTENCE):

                datapoints = []  # Collections of datapoints for this sentence.

                # Look for instances within the sentence - ensuring that you only match with individual words.
                instances = [match for pattern in reprMap.keys() for match in re.finditer("(?!\s)"+re.escape(pattern)+"((?=\W)|$)", sentence)]

                while instances:
                    # While there are instances to work on

                    inst = instances.pop()

                    for match in instances:
                        # Collect the concept names the representations relate too
                        instConcept, matchConcept = reprMap[inst.group(0)], reprMap[match.group(0)]
                        
                        relations = ontology.findRelations(domain=instConcept, target=matchConcept)
                        [datapoints.append(p) for p in createDatapoint(inst, match, relations, sentence)]

                        relations = ontology.findRelations(domain=matchConcept, target=instConcept)
                        [datapoints.append(p) for p in createDatapoint(match, inst, relations, sentence)]

                self._datapoints.append(datapoints)

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
            "content": self._content,
            "datapoints": [[point.minimise() for point in segment] for segment in self._datapoints]
        }
        path = os.path.join(folder, filename)
        with open(path, "w") as filehandler:
            filehandler.write(json.dumps(struct, indent=4))