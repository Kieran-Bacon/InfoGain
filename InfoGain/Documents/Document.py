import os, re, logging, json, logging
import itertools as tools

from InfoGain.Ontology import Ontology
from .Datapoint import Datapoint
import InfoGain.Documents.DocumentOperations as DO
from InfoGain.Documents.DocumentErrors import EmptyDocument

class Document():
    """ Representation of processable documents. """

    @classmethod
    def anaphoraResolution(cls, content: str) -> str:
        """ Resolve anaphorical issues present within the document """
        logging.warning("Anaphora resolution is not implemented")
        return content

    def __init__(self, content=None, filepath=None):
        """ Initialise the variables """

        if content:
            self._content = content
        elif filepath:
            with open(filepath) as filehandler:
                self._content = filehandler.read()
        else:
            raise EmptyDocument("Attempted to create document without content")

        self._content = Document.anaphoraResolution(self._content)
        self._datapoints = []

    def sentences(self):
        """ Return the sentences """
        return [DO.cleanSentence(s).split() for s in self._content.split(".")]

    def text(self) -> str:
        """ Return the document content """
        return self._content

    def datapoints(self, data: [[Datapoint]] = None) -> [Datapoint]:
        """
        Return the datapoints held by the document. If datapoints have been provided replace
        the currently held datapoints and record new datapoins. Function is used by the relation
        extractor to replace predicted points and remove duplocated point
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

        self._datapoints = []  # Reset any datapoints currently stored

        # Split the document by the paragraph
        for paragraph in DO.split(self._content, DO.PARAGRAPH):
            for sentence in DO.split(paragraph, DO.SENTENCE):

                datapoints = []  # Collections of datapoints for this sentence.

                # Look for instances within the sentence
                instances = [match for pattern in reprMap.keys() for match in re.finditer(re.escape(pattern), sentence)]

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