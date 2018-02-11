"""
Aim of the script is to convert the ADE dataset into an ontology, and a universal JSON
file to introduce into the Relation Extraction
"""

import re, json
from InfoGain import Ontology

ADE = Ontology(filepath="./ADE_corpus.ont")

with open("./DRUG-DOSE.rel","r") as handler:
    document = handler.read().splitlines()

points = []
for documentLine in document:
    line = documentLine.split("|")

    sentence = line[1]
    domain = line[5]
    target = line[2]

    if re.search(domain,sentence) is None: continue
    if re.search(target,sentence) is None: continue

    domain_span = re.search(domain,sentence).span()
    
    target_span = re.search(target,sentence).span()

    first = domain_span if int(domain_span[0]) < int(target_span[0]) else target_span
    second = domain_span if int(domain_span[0]) > int(target_span[0]) else target_span

    datapoint = {}
    datapoint["text"] = sentence
    datapoint["domain"] = {"concept":"Drug", "text":domain}
    datapoint["target"] = {"concept":"Dose", "text":target}
    datapoint["context"] = {"left":sentence[:int(first[0])],\
                            "middle":sentence[int(first[1]):int(second[0])],\
                            "right":sentence[int(second[1]):]}

    datapoint["relation"] = "has_dosage"
    datapoint["annotation"] = 1

    points.append(datapoint)

with open("./DRUG-DOSE.rel.datapoints", "w") as handler:
    handler.write(json.dumps({"datapoints":points}, indent=4, sort_keys=True))