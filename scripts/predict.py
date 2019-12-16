from infogain.artefact import Document, Entity, Annotation
from infogain.knowledge import Relation
from infogain.extraction import ExtractionEngine
from infogain.resources.ontologies import language

import time

start = time.time()
def timer(): print(time.time() - start)

engine = ExtractionEngine(ontology=language.ontology())
timer()

# Train the extractor
print(language.training())
for doc in language.training():
    for ann in doc.annotations:
        print(ann)

engine.fit(language.training())
timer()

# Creating the relationship friends with
person = engine.concepts["Person"]  # Collecting the person concept for relation binding
Friends = Relation({person}, "friendsWith", {person})  # Creating the relation object
engine.relations.add(Friends)  # Adding the relationship to the relation extractor

timer()

# Create a collection of documents
document_set = [
    Document(content="Kieran is a good friend of Luke."),
    Document(content="Kieran has always been good friends with Luke"),
    Document(content="Kieran has only recently became good friends with Luke.")
]
timer()
print("here")
# Annotate each of the documents within the document set
for document in document_set:
    kieran, luke = Entity('Person', 'Kieran'), Entity('Person', 'Luke')

    document.entities.add(kieran, document.content.find("Kieran"))
    document.entities.add(luke, document.content.find('Luke'))

    document.annotations.add(Annotation(kieran, 'friendsWith', luke, classification=Annotation.POSITIVE))
    document.annotations.add(Annotation(kieran, 'informs', luke, classification=Annotation.INSUFFICIENT))

timer()

engine.fit(document_set)
timer()
print('here')

corpus, scores = engine.score(language.training(), pprint=True)
print(corpus, scores)
timer()

engine.predict(
    Document(
        content = 'Kieran speaks English. Though Kieran learnt to speak English in high school, he never learn\'t french.'
    )
)
timer()