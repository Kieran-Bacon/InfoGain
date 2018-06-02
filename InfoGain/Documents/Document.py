import os, uuid, json, re, itertools

from ..Knowledge import Ontology

from .Datapoint import Datapoint
from ..Documents import DocumentOperations as DO

class Document:

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
        self._concepts = None
        
        # Save the content, overwrite provided content with read content
        self._content = content
        if filepath:
            with open(filepath) as handler:
                self._content = handler.read()

        # Clean the content of un-needed white space.
        self._content = DO.cleanWhiteSpace(self._content)

        # Maintain a collection of datapoints
        self._datapoints = []

        try:
            content = json.loads(self._content)
            self.name = content.get("name", self.name)
            self._content = content.get("content", self._content)
            #self._datapoints += [Datapoint(data) for data in content.get("datapoints",[])]
            self._datapoints = self._datapoints + [Datapoint(data) for data in content.get("datapoints",[])]
        except:
            pass

    def __len__(self):
        """ Return the assumed length of the document, the number of datapoints, if none give, the 
        length of the content """
        if self._datapoints: return len(self._datapoints)
        return len(self._content)

    def concepts(self) -> {str:str}:
        if self._concepts is None:
            self._concepts = {}

            for point in self._datapoints:
                self._concepts[point.domain["concept"]] = self._concepts.get(point.domain["concept"], []) + [point.domain["text"]]
                self._concepts[point.target["concept"]] = self._concepts.get(point.target["concept"], []) + [point.target["text"]]

        return self._concepts

    def text(self) -> str:
        """ Return the content of the document """
        return self._content
 
    def sentences(self, cleaned: bool = False) -> [str]:
        """ Split the content of the document into sentences, and return the collection of 
        sentences. """
        if self._content:
            if cleaned:
                return [DO.cleanSentence(sen) for sen in DO.split(self._content, DO.SENTENCE)]
            return DO.split(self._content, DO.SENTENCE)
        
        if self._datapoints:
            if cleaned:
                return [DO.cleanSentence(point.text) for point in self._datapoints]
            return [point.text for point in self._datapoints]

    def words(self, cleaned: bool = False) -> [[str]]:
        """ Split the content of the document into sentences and then into words. """
        if self._content:
            if cleaned:
                return [DO.cleanSentence(sen).split() for sen in DO.split(self._content, DO.SENTENCE)]
            return [sen.split() for sen in DO.split(self._content, DO.SENTENCE)]
            
        if self._datapoints:
            if cleaned:
                return [DO.cleanSentence(point.text).split() for point in self._datapoints]
            return [point.text for point in self._datapoints]

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

    def processKnowledge(self, ontology: Ontology) -> None:
        """ Iterate over the document and create potential datapoints for all possible combinations 
        of the concepts that are found.
        
        Params:
            ontology - The ontology object that contains all the information about the concepts and 
                relationships we care about
        """
        # TODO There can be a single representation that links to multiple concepts, ergo, randomly can fail.
        reprMap = {concept.name: {concept.name} for concept in ontology.concepts()}
        for concept in ontology.concepts():
            for alias in concept.alias:
                reprMap[alias] = reprMap.get(alias, set()).union({concept.name})

        # Compile the search patterns into a single pattern.
        patterns = ["(^| )"+pattern+"((?=\W)|$)" for pattern in reprMap.keys()]
        aggregatedPattern = re.compile("|".join(patterns))

        def createDatapoint(dom, domCon, tar, tarCon, relations, sentence):
            """ Generate the datapoints and add them to the document datapoint collection """ 

            p1, p2 = (dom.span(), tar.span()) if dom.span()[0] < tar.span()[0] else (tar.span(), dom.span())

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

        for sentence in DO.split(self._content, DO.SENTENCE):

            # Look for instances within the sentence - ensuring that you only match with individual words.
            instances = list(aggregatedPattern.finditer(sentence))

            while instances:
                # While there are instances to work on

                inst = instances.pop()

                for match in instances:
                    # Collect the concept names the representations relate too
                    instConcepts, matchConcepts = reprMap[inst.group(0).strip()], reprMap[match.group(0).strip()]

                    for instConcept, matchConcept in itertools.product(instConcepts, matchConcepts):
                    
                        relations = ontology.findRelations(domain=instConcept, target=matchConcept)


                        [self._datapoints.append(p) for p in createDatapoint(inst, instConcept, match, matchConcept, relations, sentence)]

                        relations = ontology.findRelations(domain=matchConcept, target=instConcept)
                        [self._datapoints.append(p) for p in createDatapoint(match, matchConcept, inst, instConcept, relations, sentence)]

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