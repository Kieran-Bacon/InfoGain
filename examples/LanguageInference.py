
from infogain.artefact import Document
from infogain.extraction import RelationExtractor
from infogain.cognition import InferenceEngine
from infogain.resources.ontologies import language

import logging
logging.basicConfig(level=logging.DEBUG)

ontologylog = logging.getLogger("infogain.knowledge")
ontologylog.setLevel(logging.ERROR)

ont = language.ontology()

extractor = RelationExtractor(ontology=ont)
extractor.fit(language.training())

Document(content="Kieran lives in England, he has done for around 10 years.")

documents = extractor.predict(Document(content="Kieran lives in England, he has done for around 10 years."))


engine = InferenceEngine("inference", ontology=ont)

print(engine.inferRelation(engine.instances("England"), "speaks", engine.instances("English")))

print(engine.inferRelation(engine.instances("Kieran"), "lives_in", engine.instances("England")))

for doc in documents:
    for point in doc.datapoints():
        print(point)

engine.addWorldKnowledge(documents)

print(engine.inferRelation(engine.instances("Kieran"), "lives_in", engine.instances("England")))