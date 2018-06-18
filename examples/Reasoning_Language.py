
from InfoGain.Documents import Document, Datapoint
from InfoGain.Knowledge import Ontology, Instance, Relation, Fact
from InfoGain.Inference import Reasoner
from InfoGain.Resources import Language

# Load the reasoner with the base ontology
engine = Reasoner(ontology=Language.ontology())

# Generate Domain information
## Concept instances
engine.addInstance(Instance("Kieran", parent="Person"))
engine.addInstance(Instance("England", parent="Country"))
engine.addInstance(Instance("France", parent="Country"))

## Define some statements of fact
fact = Fact("Kieran", "born_in", "France", 1, 0.75)

## Include some information generated from the Extraction process
point = Datapoint({
    "domain":{"concept": "Person", "text":"Kieran"},
    "relation": "lives_in",
    "target":{"concept":"Country", "text":"England"},
    "prediction": 1,
    "probability": 0.75
})
document = Document()
document.datapoints([point])

# Provide the knowledge to the reasoner
engine.knowledge(documents={document}, facts={fact})

# Evaluate an relationship
engine.evaluateRelation("Kieran", "Speaks", "English")