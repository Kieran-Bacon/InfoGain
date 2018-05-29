from InfoGain import *
from InfoGain import Resources

# Creating the language ontology
LanguageOntology = Ontology("Languages")

# Creating the concepts
person, country, language = Concept("Person"), Concept("Country"), Concept("Language")
kieran, luke = Concept("Kieran"), Concept("Luke")
england, germany, france, spain = Concept("England"), Concept("Germany"), Concept("France"), Concept("Spain")
english, german, french, spanish = Concept("English"), Concept("German"), Concept("French"), Concept("Spanish")

# Defining family membership
for con in [kieran, luke]:
    person.addChild(con)
    con.addParent(person)

for con in [england, germany, france, spain]:
    country.addChild(con)
    con.addParent(country)

for con in [english, german, french, spanish]:
    language.addChild(con)
    con.addParent(language)

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

# Saving the ontology
LanguageOntology.save("tempOnt.json")

# Create a training document
training_string = "Kieran has lived in England for a long time. Kieran can speak English rather well"
#trainingDocument = AnnotationDocument(content=training_string).annotate(LanguageOntology)

trainingDocument = TrainingDocument(filepath="./test.json")

# Collecting some other examples for better training
training = [trainingDocument] + Resources.Language.training()

# Create a document to predict
prediction_string = "Luke can speak English rather well, but Luke doesn't live in England."
testing = Document(content=prediction_string)

# Create the Relation extractor
extractor = RelationExtractor(ontology=LanguageOntology)

# Fit the training data
extractor.fit(training)

# Predict on the testing
extractor.predict(testing)

# Pring the predictions

print("Prediction content:")
print(prediction_string)

for point in [p for group in testing.datapoints() for p in group]:

    print("Relationship:", point.domainRepr, point.relation, point.targetRepr)
    print("Class:", point.prediction)
    print("Probability:", point.predProb)
    print()