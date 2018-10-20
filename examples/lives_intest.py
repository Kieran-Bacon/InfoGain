
from infogain.artefact import Document, Datapoint
from infogain.cognition import InferenceEngine
from infogain.resources.ontologies import language

# Set up logging for the example
import logging
logging.basicConfig(level=logging.DEBUG)
for model in ["infogain.knowledge", "infogain.extraction", "smart_open"]:
    log = logging.getLogger(model)
    log.setLevel(logging.ERROR)

# Import the language ontology
ont = language.ontology()

# Generate a inference engine with the basic language ontology
engine = InferenceEngine("inference", ontology=ont)

# Calculate the confidence of the speaks relationship
speaksConf = engine.inferRelation(
    engine.instances("England"),
    "speaks",
    engine.instances("English")
)
print("England speaks English is believed with confidence {}".format(speaksConf))


lives_inConf = engine.inferRelation(
    engine.instances("Kieran"),
    "lives_in",
    engine.instances("England")
)
print("Kieran lives in England has a confidence of {}".format(lives_inConf))

lives_in = Datapoint({
    "domain": {"concept": "Kieran", "text": "Kieran"},
    "relation": "lives_in",
    "target": {"concept": "German", "text": "German"},

    "prediction": 1,
    "probability": 0.69
})

doc = Document()
doc.datapoints([lives_in])

# Generate some examples of world knowledge written in unstructured form
documents = [
    doc
]

# Add the information into the inference engine
engine.addWorldKnowledge(documents)

# Calculate the impact of the new knowledge
print("\nAfter world knowledge added:")
lives_inConf = engine.inferRelation(
    engine.instances("Kieran"),
    "lives_in",
    engine.instances("England")
)
print("Kieran lives in England has a confidence of {}".format(lives_inConf))