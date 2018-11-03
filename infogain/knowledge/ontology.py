import os, uuid, logging, json

from ..exceptions import MissingConcept
from .concept import Concept
from .relation import Relation
from .rule import Rule

log = logging.getLogger(__name__)

class Ontology:
    """ An ontology is a collection of knowledge, it contains a collection of concepts
    and the relationships between them.

    Args:
        name (str): The name given to the ontology
        filepath (str): The location of a saved ontology to expand
    """

    def __init__(self, name: str = None, filepath: str = None):

        # Simply idenfitication of the ontology, no functional use
        self.name = name
        self._concepts = {}                     # Unique concept store
        self._builtins = {}                     # Unique built in concept store
        self._relations = {}                    # Unique relation store

        self._missedConcepts = {}               # Mapping between incomplete concepts

        self._importedmodules = []              # Keep track of the imported builtin modules

        if filepath:

            # Extract the information from the input ontology file
            with open(filepath) as ontologyFile:
                data = json.load(ontologyFile)

            # Define the name
            if "Name" in data: self.name = data["Name"]

            # Create the concepts and add them to the ontology store without warnings
            for name, rawConcept in data.get("Concepts", {}).items():
                log.debug("adding concept {}".format(name))
                concept = Concept(name, json=rawConcept)
                self.addConcept(concept)
                    
            # Create the relations within the system
            for name, rawRelation in data.get("Relations", {}).items():
                log.debug("adding relation {}".format(name))

                rules = []
                for desc in rawRelation.get("rules", []):
                    rules.append(Rule(**desc))

                relation = Relation(
                    rawRelation["domains"],
                    name,
                    rawRelation["targets"],
                    rules,
                    rawRelation.get("differ", False)
                )

                self.addRelation(relation)

    def importBuiltin(self, module_name: str) -> None:
        """ Import knowledge considered common (and required) in most applications. Add the

        Params:
            module_name (str): The builtin title
        """
        import importlib

        try:
            module = importlib.import_module("infogain.knowledge.builtin_concepts.{}".format(module_name))
            [self.addConcept(con) for con in module.concepts()]
        except ImportError as e:
            msg = "ImportError - No builtin module by that name: {}".format(module_name)
            log.error(msg, exc_info=True)
            raise ImportError(msg)

    def addConcept(self, concept: Concept) -> None:
        """ Add concept object to ontology, overwrite previous concept if present.
        Identifies the relation ships concepts parent objects are and becomes members to those
        relations if applicable. 
        
        Params:
            concept (Concept) - The concept to add
        """

        for relative in concept.parents.union(concept.children):

            if isinstance(relative, Concept): relative = relative.name

            found = self.concept(relative)
            if found:
                Concept.fuse(concept, found)
            else:
                missedSet = self._missedConcepts.get(relative, set())
                missedSet.add(concept)
                self._missedConcepts[relative] = missedSet

        if concept.name in self._missedConcepts:


            [Concept.fuse(concept, relative) for relative in self._missedConcepts[concept.name]]
            del self._missedConcepts[concept.name]

        self._concepts[concept.name] = concept
        [relation.subscribe(concept) for relation in self._relations.values()]

    def _addMissingConcept(self, concept: Concept, missing_concept: str, parentOf: bool) -> None:
        """ Add a concept name in as a missing concept in preparation of the concept or
        add to the missing concept information if the concept has been references numerous times

        Params:
            concept (str): The name of the concept that is missing
            missing_concept (str): The name of the concept that is missing
            parentOf (str): Indicator of relationship, parent or child.
        """
        record = self._missedConcepts.get(missing_concept, {"parents":{}, "children": {}})
        if parentOf:
            record["children"].add(concept)
        else:
            record["parents"].add(concept)

    def addRelation(self, relation: Relation) -> Relation:
        """ Add a new relation object to the ontology, correctly link the relation concepts to the 
        ontology.
        
        Params:
            relation (Relation) - The relation object to add to the ontology

        Returns:
            Relation - The original relation or a newly generated relation with edits.
        """

        if any([isinstance(con, str) for con in relation.domains.union(relation.targets)]):
            minimised = relation.minimise()
            minimised["domains"] = [[self.concept(dom) for dom in group] for group in minimised["domains"]]
            minimised["targets"] = [[self.concept(tar) for tar in group] for group in minimised["targets"]]

            rules = []
            for rule in minimised.get("rules", []):
                rule["domains"] = [self.concept(con) for con in rule["domains"]]
                rule["targets"] = [self.concept(con) for con in rule["targets"]]
                rules.append(Rule(**rule))

            minimised["rules"] = rules

            relation = Relation(**minimised)

        log.debug("Added Relation {}".format(str(relation)))
        self._relations[relation.name] = relation
        return relation

    def concept(self, conceptName: str) -> Concept:
        """ Collect the ontology concept with the name given, or None """
        return self._concepts.get(conceptName)

    def concepts(self) -> [Concept]:
        """ Return a list of concepts found within the ontology, order is non deterministic """
        return list(self._concepts.values())

    def relation(self, relationName: str) -> Relation:
        """ Collect the relation objects for name given, or None """
        return self._relations.get(relationName)

    def relations(self, names=False) -> [str]:
        """ Return the ontology relations or the names of all the relations 
        
        Params:
            keys (bool) - Toggle for the names of the relations or the relations themselves
        
        Returns:
            [str] - A list of names of the relations or a list of relation objects
        """
        if names: return list(self._relations.keys())
        else:     return list(self._relations.values())

    def findRelations(self, domain: str, target: str) -> [Relation]:
        """ Return a list of relations that could be formed between the domain and the target 
        objects. Yield the relations.
        
        Params:
            domain (str) - A concept that needs to match with the domain of potential relations
            target (str) - A concept that needs to match with the target of potential relations
        """

        dom = self.concept(domain) if isinstance(domain, str) else domain
        tar = self.concept(target) if isinstance(target, str) else target
        if None in (dom, tar):
            raise Exception("Invalid concepts provided when looking for relations")

        for relation in self.relations():
            if relation.between(dom, tar):
                yield relation

    def clone(self):
        """ Create a new ontology object that is a deep copy of this ontology instance 
        
        Returns:
            clone (Ontology) - A deep copy of this ontology object
        """

        ontologyClone = Ontology(self.name)

        # Clone concepts
        [ontologyClone.addConcept(con.clone()) for con in self.concepts()]
        [ontologyClone.addRelation(rel.clone()) for rel in self.relations()]

        return ontologyClone

    def toJson(self):
        """ Save the file to the current working directory or the filename provided
        
        Params:
            folder (str) - The directory destination of the saved file
            filename (str) - The name to be given to the saved file
        """
                    
        ontology = {
            "Name": self.name,
            "Concepts": {},
            "Relations": {}
        }

        for name, concept in self._concepts.items():
            mini = concept.minimise()
            del mini["name"]
            ontology["Concepts"][name] = mini

        for name, relation in self._relations.items():
            mini = relation.minimise()
            del mini["name"]
            ontology["Relations"][name] = mini

        return json.dumps(ontology, indent=4, sort_keys=True)

    def save(self, folder: str = "./", filename: str = None) -> None:

        if filename is None and self.name is None: filename = uuid.uuid4().hex
        if self.name and not filename: filename = self.name

        with open(os.path.abspath(os.path.join(folder, filename)), "w") as handler:
            handler.write(self.toJson())