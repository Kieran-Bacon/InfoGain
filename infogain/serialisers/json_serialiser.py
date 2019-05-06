import json

from ..knowledge import Ontology, Concept, Relation, Rule, Condition
from .serialiser import AbstractSerialiser, registerSerialiser

@registerSerialiser("json")
class JsonSerialiser(AbstractSerialiser):

    def load(self, filepath: str):

        # Extract the information from the input ontology file
        try:
            with open(filepath) as ontologyFile:
                data = json.load(ontologyFile)
        except Exception as e:
            raise RuntimeError("Failed parser json document found at {}".format(filepath)) from e

        # Create an empty ontology object
        ontology = Ontology(name = data.get("Name"))

        # Load concept information
        for name, conceptData in data.get("Concepts", {}).items():
            # Upack the concept data into the concept init
            ontology.concepts.add(Concept(name, **conceptData))

        # Load relation information
        for name, rawRelation in data.get("Relations", {}).items():
            # First process the relation rule and conditions
            rules = []
            for definition in rawRelation.get("rules", []):
                # Convert the conditions into their respective condition objects
                if "conditions" in definition:
                    definition["conditions"] = [
                        Condition(cond["logic"], cond["salience"]) for cond in definition["conditions"]
                    ]

                # Generate and add the rules
                rules.append(Rule(
                    **definition
                ))

            # Generate and add the relation object to the ontology
            ontology.relations.add(
                Relation(
                    rawRelation["domains"],
                    name,
                    rawRelation["targets"],
                    rules=rules,
                    differ=rawRelation.get("differ", False)
                )
            )


        return ontology

    def dump(self, ontology: Ontology):

        ontology_dict = {
            "Name": ontology.name,
            "Concepts": {},
            "Relations": {}
        }

        # for name, concept in ontology._concepts.items():
        #     mini = concept.minimise()
        #     del mini["name"]
        #     ontology_dict["Concepts"][name] = mini

        # for name, relation in ontology._relations.items():
        #     mini = relation.minimise()
        #     del mini["name"]
        #     ontology_dict["Relations"][name] = mini

        return json.dumps(ontology_dict, indent=4, sort_keys=True)