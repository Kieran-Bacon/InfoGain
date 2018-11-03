from infogain.knowledge import *

schoolOntology = Ontology("School")

person = Concept("Person", properties={"age": None})
_class = Concept("Class", properties={"length": None, "subject": None})
beingTheoldesInClass = Concept("Oldest", category="static")

rel_attends = Relation({person}, "attends", {_class})

rel_oldest = Relation({person}, "isOldestWithin", {_class}, rules=[
    Rule({person}, {_class}, 100, conditions = [
        {"logic": "#Person=attends=@", "salience": 100},
        {"logic": "f(%.age, #Person.age, (x > y)*100)", "salience": 100}
    ])
])




#a person is the oldes in a class if their age is greater than all the other students ages.





