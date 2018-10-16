
from infogain.artefact import Document
from infogain.extraction import RelationExtractor
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

# Generate a relation extractor 
extractor = RelationExtractor(ontology=ont)
extractor.fit(language.training())

# Generate some examples of world knowledge written in unstructured form
documents = [
    Document(content="Kieran lives in England, he has done for around 10 years.")
]

# Extract the information from the world knowledge
documents = extractor.predict(documents)

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