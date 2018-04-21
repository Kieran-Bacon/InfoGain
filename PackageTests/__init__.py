import os

LOCATION = os.path.dirname(os.path.realpath(__file__))
DOCUMENTS = os.path.join(LOCATION, "Resources", "Documents")
ONTOLOGIES = os.path.join(LOCATION, "Resources", "Ontologies")
LANGUAGE_ONTOLOGY = os.path.join(LOCATION, "Resources", "Ontologies","languages.json")

PATHS = {
    "language":{
        "ontology": os.path.join(ONTOLOGIES, "languages.json"),
        "training": [os.path.join(DOCUMENTS,"language","training","tr1.json")],
        "prediction": [os.path.join(DOCUMENTS,"language","prediction","pr1.txt")]
    },
    "medicine":{
        "ontology": os.path.join(ONTOLOGIES, "medical.json"),
        "training": [os.path.join(DOCUMENTS, "medicine", "training",  "tr1.json")],
        "prediction": [os.path.join(DOCUMENTS, "medicine", "prediction", "pr1.txt")]
    }
}