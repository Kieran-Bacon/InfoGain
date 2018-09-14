from ..Knowledge import Ontology, Relation

class InferenceEngine(Ontology):
    """ Through a collection of knowledge, infer information that is consitent with what is known
    stating confidence in the inference as we produce it """

    def __init__(self, name:str = None, filepath:str=None, ontology:Ontology=None):

        if ontology:
            ont = ontology.clone()
            self.name = name if name else ont.name
            self._concepts = ont._concepts
            self._relations = ont._relations

        if filepath:
            Ontology.__init__(name, filepath=filepath)

    def inferRelation(self, relation: Relation):
        pass

    
