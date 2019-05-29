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
            # Unpack the concept data into the concept init
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

        # Minimise the ontology concepts
        for concept in ontology.concepts():

            # The minimised json serialisable concept data
            minimised_concept = {}

            if concept.parents:
                minimised_concept["parents"] = sorted(
                    [parent if isinstance(parent, str) else parent.name for parent in concept.parents]
                )

            if concept.properties:
                minimised_concept["properties"] = concept.properties.copy()

            if concept.aliases:
                minimised_concept["alias"] = sorted(concept.aliases)

            if concept.category is not Concept.DYNAMIC:
                minimised_concept["category"] = concept.category

            ontology_dict["Concepts"][concept.name] = minimised_concept

        # Minimise the ontology relations into json serialisable objects
        for relation in ontology.relations():


            minimised_relations = {
                "domains": sorted([group.minimised().toStringSet() for group in relation.concepts.domains]),
                "targets": sorted([group.minimised().toStringSet() for group in relation.concepts.targets])
            }

            # Record non-default parameters
            if relation.differ: minimised_relations["differ"] = True

            if relation.rules:

                rules = []
                for rule in relation.rules:

                    minimised_rule = {
                        "domains": sorted(rule.domains.bases.toStringSet()),
                        "targets": sorted(rule.targets.bases.toStringSet()),
                        "confidence": rule.confidence
                    }

                    if rule.conditions:
                        minimised_rule["conditions"] = [
                            {"logic": condition.logic, "salience": condition.salience} for condition in rule.conditions
                        ]

                    if not rule.supporting: minimised_rule["supporting"] = rule.supporting

                    rules.append(minimised_rule)

                minimised_relations["rules"] = rules

            ontology_dict["Relations"][relation.name] = minimised_relations

        return json.dumps(ontology_dict, indent=4, sort_keys=True)