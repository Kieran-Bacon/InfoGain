from .ontology import Ontology as ConcreteOntology
from .concept import Concept as ConcreteConcept
from .instance import Instance as ConcreteInstance
from .relation import Relation as ConcreteRelation
from .rule import Condition, Rule as ConcreteRule

class Concept:

    def __new__(self, name):

        # Extract concept information
        conceptInfo = ["alias", "properties", "category"]
        info = {}
        for key in conceptInfo:
            if key in self.__dict__:
                info[key] = self.__dict__[key]

        # Extract the parent information
        instanceInfo = {}
        parents = set()
        for base in self.__bases__:
            if base.__name__ != "Concept": parents.add(base.__name__)
            instanceInfo.update(base.__dict__)

        instanceInfo.update(self.__dict__)
        instanceClass = type(name, (ConcreteInstance,), {k:v for k, v in instanceInfo.items() if k not in conceptInfo})

        concept = ConcreteConcept(name, **info, parents=parents)
        concept.setInstanceClass(instanceClass)

        return concept



class Relation:

    domains = None
    targets = None
    rules = []
    differ = False

    def __new__(self, name, ontology: ConcreteOntology):
        rules = [rule.makeConcrete(ontology) for rule in self.rules]
        return ConcreteRelation(self.domains, name, self.targets, rules=rules, differ=self.differ)

class Rule:
    def __init__(
        self,
        domains,
        targets,
        confidence,
        *,
        supporting: bool = True,
        conditions: [Condition] = []
        ):

        self.concepts = {
            "domains": domains if not isinstance(domains, str) else {domains},
            "targets": targets if not isinstance(targets, str) else {targets}
        }
        self.confidence = confidence
        self.supporting = supporting
        self.conditions = conditions

    def makeConcrete(self, ontology: ConcreteOntology):

        concepts = {"domains": set(), "targets": set()}
        for setname, group in self.concepts.items():
            for con in group:
                concept = ontology.concept(con)
                if concept: concepts[setname].add(concept)
                else: raise ValueError("Rule contains reference to an unknown concept {}".format(con))

        return ConcreteRule(**concepts, confidence=self.confidence, supporting=self.supporting, conditions=self.conditions)

class Ontology:

    @classmethod
    def build(cls) -> ConcreteOntology:

        # Create an ontology object
        ontologyInstance = ConcreteOntology()

        # Loop through the attributes of this class definition to find the definitions for the concepts and relations
        relations = []
        for attrName in [attr for attr in dir(cls) if not attr.startswith("__") and attr != "build"]:
            attr = getattr(cls, attrName)

            if issubclass(attr, Concept):
                conceptInstance = attr(attrName)  # Create the concept from this definition
                ontologyInstance.addConcept(conceptInstance)  # Add it immediately to the ontology

            elif issubclass(attr, Relation):
                # Record the relations in a separate structure for when all the concepts have been added to the ontology
                relations.append((attrName, attr))

        # For all of the relation definitions, add them in now that the concepts have been completed
        for name, relationClass in relations:
            relationInstance = relationClass(name, ontologyInstance)
            ontologyInstance.addRelation(relationInstance)

        return ontologyInstance