# Ontology

## Adding concepts

A concept that is added to an ontology is then linked with any ontology member concept that the concept has a partial connection too. The added concept doesn't have its concrete parent/children checked for membership to the ontology. It is assumed that only one concept shall ever be created with that name. The ontology does not protect against poor coding interweaves two ontologies together simultaneously.

## Concepts

### Concept attributes

Concepts properties are inherited by child concepts as it should be true that a property of a type should be true for all concepts that are of that type. However, blindly inheriting properties can lead to inconsistencies in the ontology when it comes to multiple inheritance. Though it may be true that a concept is a type of something, it may have a property given by a different parent. It is impossible to discern which property should be choosen in these events, such that the choice is left up to the user. All conflicting attributes shall be kept and given when asking for these values. The intention is that in such events the user is to choose and give the correct value for the concept property.

A multipart object shall be created for these properties to house the multiple values given. A user would be wise to set a specific value for the property on the concept itself to avoid any issues that this might cause.

```python
a = Concept("A", properties={"example": 1})
b = Concept("B", properties={"example": 2})

c = Concept("C", parents={a, b})

c.properties["example"]
>'<MultiPartProperty(1, 2)>'

c.properties["example"] = 2

c.properties["example"]
>'2'
```


 A concept that inherits multiple concepts that have differing values for a property, discerning which one is the correct property to exhibit is rather difficult to .

### Removing a concept from a family set

This is simple, sorry about this, I am thinking about what happens when you remove a concept from a relation concept set... that shit gets weird real quick mudda

If a concept is either of its parents of children removed, the relationships are not updated/informed of the change. They have not performed any caching that shall be inconsistent with the change made to the concept.

However... The ConceptSets that the relationship holds, shall continue to contain all of the concepts that it used to. As in

a - 1
b   2

|-------|
b   a - 1
        2

is still true...

## Relations

Relations cascade down on both the domains and target concepts as potential targets. Abstract concepts are included to hold the hierarchy only, they cannot be member of a relationship, and they
aren't returned when

### Adding concepts to the relation

```python

Relation([[x],[y]], "name", [[x,y],[z]])

rel.between(x, z) # False

relation.domain.add(x, 1)

relation.domains()

relation.domains.add(Concept())
relation.domains.add(Concept(), 1)

for domains, targets in relation.concepts:

for domains in




for domain, targets in relation.concepts:
    if x < y:
        domain.add(Concept("what"))

```


```python

>>>relation.rules
[Rule, Rule, Rule]

>>>relation.rules(domain, target)
[Rule, Rule]

>>>relation.rules.add(Rule)

>>>relation.rules[0] = Rule


```

Though it is possible to add partial concepts to the relation - it cannot have partial concepts as a member which are inherited by parent concepts. These concepts must be resolved before hand.

## Rule

```python

rule.domains.add("Concept")
rule.targets.add("Concept\"This is a lot better")

rule.conditions.add(Condition)

if rule.conditions:


for condition in rule.conditions:
    do_stuff()

# Alternatively



rule.addCondition(Condition("this is a condition"))

rule.conditions
```