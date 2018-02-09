"""
Aim of the script is to convert the ADE dataset into an ontology, and a universal JSON
file to introduce into the Relation Extraction
"""

import re
from InfoGain import Ontology, Concept, Relation

ADE = Ontology("Hey", "./ADE.json")

drugOntology = Ontology("ADE")
drug, dose, effect = Concept("Drug"), Concept("Dose"), Concept("Adverse Effect")

drugOntology.addConcept(drug)
drugOntology.addConcept(dose)
drugOntology.addConcept(effect)

drugOntology.addRelation(Relation({drug},"hasAffect",{effect}))
drugOntology.addRelation(Relation({drug},"hasDose",{dose}))

with open("./DRUG-DOSE.rel","r") as handler:
    document = handler.read().splitlines()

points = []
for documentLine in document:
    line = documentLine[0].split("|")

    sentence = line[1]
    domain = line[2]
    domain_span = re.search(domain,sentence).span()
    target = line[5]
    target_span = re.search(target,sentence).span()

    first = domain_span if int(domain_span[0]) < int(target_span[0]) else target_span
    second = domain_span if int(domain_span[0]) > int(target_span[0]) else target_span

    datapoint = {}
    datapoint["domain"] = domain
    datapoint["target"] = target
    datapoint["leading words"] = sentence[:int(first[0])])
    datapoint["concept 1"] = sentence[int(first[0]):int(first[1])]
    datapoint["inter words"] = sentence[int(first[1]):int(second[0])])
    datapoint["concept 2"] = sentence[int(second[0]):int(second[1])]
    datapoint["trailing words"] = sentence[int(second[1]):])

    points.append(datapoint)
    
