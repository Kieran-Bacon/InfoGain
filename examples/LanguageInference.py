from infogain.cognition import InferenceEngine
from infogain.resources.ontologies import language

import logging
logging.basicConfig(level=logging.DEBUG)

ontologylog = logging.getLogger("infogain.knowledge")
ontologylog.setLevel(logging.ERROR)

ont = language.ontology()

rel = ont.relation("speaks")

engine = InferenceEngine("inference", ontology=ont)

newRel = engine.relation("speaks")

print(engine.inferRelation("England", "speaks", "English"))

print(engine.inferRelation("Kieran", "lives_in", "England"))

print("Eval", engine.inferRelation(engine.concept("Kieran"), "speaks", engine.concept("English")))

print(engine.inferRelation("Kieran", "lives_in", "England"))