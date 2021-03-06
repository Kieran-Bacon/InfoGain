import logging

logging.basicConfig(level=logging.DEBUG)

from infogain.knowledge import Ontology, Concept, Relation
from infogain.extraction import RelationExtractor
from infogain.artefact import Document, annotate, score

#from InfoGain.Resources import Language
from infogain.resources.ontologies import language as Language

# Creating the language ontology
LanguageOntology = Ontology("Languages")

# Creating the concepts
person = Concept("Person", children={"Kieran", "Luke"})
kieran, luke = Concept("Kieran", parents={"Person"}), Concept("Luke", parents={"Person"})

country = Concept("Country", children={"England","Germany","France","Spain"})
england, germany = Concept("England", parents={country}), Concept("Germany", parents={country})
france, spain = Concept("France",{country}), Concept("Spain",{country})

language = Concept("Language", children={"English", "German", "French", "Spanish"})
english, german = Concept("English", parents={language}), Concept("German", parents={language})
french, spanish = Concept("French", parents={language}), Concept("Spanish", parents={language})

# Adding concepts to the ontology
for concept in [person, country, language, kieran, luke, england, english, germany, german, france, french, spain, spanish]:
    LanguageOntology.addConcept(concept)

# Define some relations 
speaks = Relation({person}, "speaks", {language})
born_in = Relation({person}, "born_in", {country})
lives_in = Relation({person}, "lives_in", {country})

# Add the relation to the ontology
for relation in [speaks, born_in, lives_in]:
    LanguageOntology.addRelation(relation)

# Create a training document
training_string = "Kieran has lived in England for a long time. Kieran can speak English rather well"
trainingDocument = annotate(LanguageOntology, [Document(content = training_string)])

# Collecting some other examples for better training
training = [trainingDocument] + Language.training()

# Create a document to predict
prediction_string = "Luke can speak English rather well, but Luke doesn't live in England."
testing = Document(content=prediction_string)

# Create the Relation extractor
extractor = RelationExtractor(ontology=LanguageOntology, min_count=1)

# Fit the training data
extractor.fit(training)

# Predict on the testing
extractor.predict(testing)

# Print the predictions
print("Prediction content:")
print(prediction_string)

corpus, _ = score(extractor, testing)
print("Testing score:", corpus)
[print(point) for point in testing.datapoints()]