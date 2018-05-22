import os, re, logging, json
import itertools as tools

from InfoGain.Ontology import Ontology
from .Datapoint import Datapoint
import InfoGain.Documents.DocumentOperations as DO

class Document():
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

    def sentences(self):
        """ Return the sentences """
        return [DO.cleanSentence(s).split() for s in self._content.split(".")]

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
                        "left": sentence[:p1[0]].strip(),
                        "middle": sentence[p1[1]:p2[0]].strip(),
                        "right": sentence[p2[1]:].strip()
                    }
                })

                # Record the new datapoint
                self._datapoints.append(dp)

        # Split the document by the paragraph
        for paragraph in DO.split(self._content, DO.PARAGRAPH):
            for sentence in DO.split(paragraph, DO.SENTENCE):

                # Look for instances within the sentence
                instances = [match for pattern in reprMap.keys() for match in re.finditer(re.escape(pattern), sentence)]

                while instances:
                    # While there are instances to work on

                    inst = instances.pop()

                    for match in instances:
                        try:
                            instConcept, matchConcept = reprMap[inst.group(0)], reprMap[match.group(0)]
                        except:
                            print("Document Error")
                            print(sentence)
                            raise ValueError
                        
                        relations = ontology.findRelations(domain=instConcept, target=matchConcept)
                        createDatapoint(inst, match, relations, sentence)

                        relations = ontology.findRelations(domain=matchConcept, target=instConcept)
                        createDatapoint(match, inst, relations, sentence)