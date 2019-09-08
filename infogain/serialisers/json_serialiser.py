import json
import collections
import uuid

from ..artefact import Document, Entity, Annotation
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

            if concept.properties._elements:
                minimised_concept["properties"] = concept.properties._elements.copy()

            if concept.aliases:
                minimised_concept["alias"] = sorted(concept.aliases)

            if concept.category is not Concept.DYNAMIC:
                minimised_concept["category"] = concept.category

            ontology_dict["Concepts"][concept.name] = minimised_concept

        # Minimise the ontology relations into json serialisable objects
        for relation in ontology.relations():


            minimised_relations = {
                "domains": [sorted(group.minimised().toStringSet()) for group in relation.domains],
                "targets": [sorted(group.minimised().toStringSet()) for group in relation.targets]
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
                        minimised_rule["conditions"] = sorted(
                            [{"logic": cond.logic, "salience": cond.salience} for cond in rule.conditions],
                            key = lambda x: (x["salience"], x["logic"])
                        )

                    if not rule.supporting: minimised_rule["supporting"] = rule.supporting

                    rules.append(minimised_rule)

                minimised_relations["rules"] = rules

            ontology_dict["Relations"][relation.name] = minimised_relations

        return json.dumps(ontology_dict, indent=4, sort_keys=True)

@registerSerialiser("json", _type = Document)
class JsonDocumentSerialiser(AbstractSerialiser):

    def load(self, filepath: str):

        # Load in the json serialised data
        with open(filepath, "r") as handle:
            data = json.load(handle)

        def resolveDocumentsContents(docData):

            if "content" in docData:
                doc = Document(docData['content'], name=docData.get('name'), text_break=docData.get('breaktext'), processed=True)
            else:
                doc = Document(name=docData.get('name'), text_break=docData.get('breaktext'), processed=True)

                for document in data['documents']:
                    doc._sub_documents.append(resolveDocumentsContents(document))

            return doc

        # Resolve the content of the document
        document = resolveDocumentsContents(data)

        # Load in the entities
        entities = {}
        for i, entityData, guid in data['entities']:
            props = entityData.pop("properties", {})
            e = Entity(**entityData)
            e.properties.update(props)
            entities[guid] = e
            document.entities.add(e, i)

        # Load in the annotations
        for ann in data['annotations']:
            document.annotations.add(
                Annotation(
                    entities[ann['domain']],
                    ann['name'],
                    entities[ann['target']],
                    classification=ann['classification'],
                    confidence=ann['confidence'],
                    annotation=ann['annotation']
                )
            )

        return document

    def dump(self, document: Document):

        def minimiseContent(subDocument):

            data = collections.OrderedDict((
                ("name", subDocument.name),
                ("breaktext", subDocument.breaktext),
            ))

            if subDocument._content is not None:
                data['content'] = subDocument.content

            else:
                data['documents'] = [
                    minimiseContent(doc) for doc in subDocument._sub_documents
                ]

            return data

        data = minimiseContent(document)
        data.pop("breaktext")

        entityIDs = collections.defaultdict(lambda: str(uuid.uuid4()))

        data['entities'] = []
        for i, e in document.entities.indexes():
            entityData = {
                "classType": e.classType,
                "surfaceForm": e.surfaceForm,
                "confidence": e.confidence,
                "properties": e.properties._elements
            }
            data['entities'].append((i, entityData, entityIDs[e]))

        data['annotations'] = []
        for annotation in document.annotations:
            data['annotations'].append({
                "domain": entityIDs[annotation.domain],
                "name": annotation.name,
                "target": entityIDs[annotation.target],

                "classification": annotation.classification,
                "confidence": annotation.confidence,
                "annotation": annotation.annotation
            })


        return json.dumps(data, indent=4)