a = "Well this is the thing something elses, Kieran's bucket.\nWell this is interesting."







import os
from InfoGain import Ontology, Document, TrainingDocument

LOCATION = os.path.dirname(os.path.realpath(__file__))
DOCUMENTS = os.path.join(LOCATION, "Resources", "Documents")
ONTOLOGIES = os.path.join(LOCATION, "Resources", "Ontologies")

ont = Ontology(filepath=os.path.join(ONTOLOGIES, "languages.json"))
doc = Document(filepath=os.path.join(DOCUMENTS, "Predictlanguages.txt"))

print(doc.context)

doc.processKnowledge(ont)
print()
for point in doc.datapoints():
    print(point.domain, point.relation, point.target)
    print(point)