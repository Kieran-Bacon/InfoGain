import logging, json

from .Ontology import Ontology
from .RelationExtractor import Datapoint

class Document():
    """ Representation of processable documents. """

    def __init__(self, ontology: Ontology):
        pass

    def sentenceEmbed(sentence: str) -> [int]:
        """ Convert the sentence into a vector """
        return [len(sentence)]*300

class TrainingDocument(Document):

    def __init__(self, ontology: Ontology, content = None, filepath = None):
        self.ontology = ontology # Storage a reference to the ontology
        self.datapoints = set()

        if not filepath is None:
            with open(filepath) as filehandler:
                content = json.load(filehandler)

        if (content and filepath) is None:
            logging.warning("No content provided in document initialisation")

        for data in content["datapoints"]:
            try:
                # Assign text representations to the concepts
                self.ontology.concept(data["domain"]["concept"]).addRepr(data["domain"]["text"])
                self.ontology.concept(data["target"]["concept"]).addRepr(data["target"]["text"])

                # Convert and save the datapoint
            
                self.datapoints.add(Datapoint(ontology, data))
            except:
                logging.warning("Corrupted datapoint found :: %s", str(data))

