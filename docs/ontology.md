# Ontology

## Adding concepts

A concept that is added to an ontology is then linked with any ontology member concept that the concept has a partial connection too. The added concept doesn't have its concrete parent/children checked for membership to the ontology. It is assumed that only one concept shall ever be created with that name. The ontology does not protect against poor coding interweaves two ontologies together simultaneously.


## Concepts

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
relation.concepts.addDomain(Concept("Kieran"))  # This shall add "Kieran" to all domains groups
relation.concepts.addDomain(Concept("Bacon"), 1)  # This shall add "Bacon to the second domain group
relation.concepts.addDomain(Concept("stop..."), 100000) # This shall create a fuck ton of sets and add this concept to the end of it...

relation.concepts.add(domain, target)  # Add this domain and range to all groups
relation.concepts.add(domain, target, 1)  # Add this domain and target to this set
```

```python

for domains, targets in relation.concepts:
    do_stuff()

domains, targets = relation.concepts[0]

domains = relation.concepts.domains[0]
```
