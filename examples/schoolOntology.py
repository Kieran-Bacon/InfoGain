from infogain.artefact import Entity, Annotation, Document
from infogain.knowledge import *
from infogain.extraction import ExtractionEngine

# Define the ontology base
schoolOntology = Ontology("School")

# Define concepts
person = Concept("Person")
_class = Concept("Class")
beingTheoldesInClass = Concept("Oldest", category="static")

for con in [person, _class, beingTheoldesInClass]: schoolOntology.concepts.add(con)

# Define the relationships
rel_attends = Relation({person}, "attends", {_class})
rel_oldest = Relation({person}, "isOldestWithin", {_class}, rules=[
    Rule({person}, {_class}, 100, conditions = [
        Condition("#Person=attends=@"),
        Condition("f(%.age, #Person.age, (x > y)*100)")
    ])
])

for rel in [rel_attends, rel_oldest]: schoolOntology.relations.add(rel)

# Define the example documents - training + test

training = Document(
    "Kieran attends an english class in the evenings. He's enjoying the class, but, its very late int he evening..."
)

kieran, english = Entity("Person", "Kieran"), Entity("Class", "english class")

training.entities.add(kieran)
training.entities.add(english, 18)
training.annotations.add(Annotation(kieran, "attends", english, annotation=Annotation.POSITIVE))
training.annotations.add(Annotation(kieran, 'isOldestWithin', english, annotation=Annotation.INSUFFICIENT))

testing = Document(
    "I think that Kieran attends an english class at UCL after work. I've overheard him talking about it."
)

# Create extraction engine for this
extraction = ExtractionEngine(ontology=schoolOntology)
extraction.fit(training)

print(list(extraction.concepts.keys()))
print(extraction.concepts['Person'].aliases)

testing = extraction.predict(testing)


print("Entities:")
for entity in testing.entities:
    print(entity)

print("Annotations:")
for ann in testing.annotations:
    print(ann)

#a person is the oldes in a class if their age is greater than all the other students ages.





