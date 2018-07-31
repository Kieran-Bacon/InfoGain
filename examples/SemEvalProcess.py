import os, re

from InfoGain.Knowledge import Ontology, Concept, Relation
from InfoGain.Documents import Document, Datapoint, score
from InfoGain.Extraction import RelationExtractor

import matplotlib.pyplot as plt

def process_section(sentence):

    text, info = sentence.split("\n")[:2]

    text = text[5:-1]

    e1 = re.search("<e1>.+</e1>", text)

    span1 = e1.span()
    e1 = e1.group(0)[4:-5]

    e2 = re.search("<e2>.+</e2>", text)
    span2 = e2.span()
    e2 = e2.group(0)[4:-5]

    (first, second) = (span1, span2) if span1[0] < span2[0] else (span2, span1)

    left, middle, right = text[:first[0]], text[first[1]:second[0]], text[second[1]:]

    text = re.sub(r"<[/]*\w\d>", "", text)

    info = re.findall(r'[\w-]+\(.+?[^)]+\) = ".+?"', info)[-1]
    relation, order, value = re.findall(r'[\w-]+(?=\()|\(.+?\)|".+?"', info)

    order = order[1:-1].split(",")
    if order[0] == "e1":
        domain, target = e1, e2
    else:
        domain, target = e2, e1

    value = 1 if value[1:-1] == "true" else -1

    sentence = {
        "domain": domain,
        "target": target,
        "relation": relation,
        "value": value,
        "text": text,
        "context": {
            "left": left,
            "right": right,
            "middle": middle,
        }
    }

    return sentence

def buildTraining():

    concepts, relations = set(), {}

    with open("./SemEval2007/TrainingSet.txt", errors='replace') as handler:

        # Read content
        content = handler.read().split("\n\n")
        datapoints = []


        for point in content:
            if point == "": continue

            point = process_section(point)
            concepts.add(point["domain"])
            concepts.add(point["target"])

            if not point["relation"] in relations:
                relations[point["relation"]] = {"domains":set(), "targets":set()}

            relations[point["relation"]]["domains"].add(point["domain"])
            relations[point["relation"]]["targets"].add(point["target"])

            point["domain"] = {"concept": point["domain"], "text": point["domain"]}
            point["target"] = {"concept": point["target"], "text": point["target"]}

            datapoint = Datapoint(point)
            datapoint.annotation = point["value"]
            datapoints.append(datapoint)

    document = Document()
    document.datapoints(datapoints)
    document.save(folder="./SemEval2007", filename="training.json")
    
    ontology = Ontology()

    for concept in concepts:
        ontology.addConcept(Concept(concept))

    for name, info in relations.items():
        domains = [ontology.concept(con) for con in info["domains"]]
        targets = [ontology.concept(con) for con in info["targets"]]
        ontology.addRelation(Relation(set(domains), name, set(targets)))

    ontology.save(folder="./SemEval2007", filename="ontology.json")

    return ontology, document

def buildTesting():

        datapoints = []

        with open("./SemEval2007/TestingSet.txt", errors='replace') as handler:

            # Read content
            content = handler.read().split("\n\n")

            for point in content:
                if point == "": continue

                point = process_section(point)
                point["domain"] = {"concept": point["domain"], "text": point["domain"]}
                point["target"] = {"concept": point["target"], "text": point["target"]}

                datapoint = Datapoint(point)
                datapoint.annotation = point["value"]
                datapoints.append(datapoint)

        document = Document()
        document.datapoints(datapoints)
        document.save(folder="./SemEval2007", filename="testing.json")
        return document

if __name__ == "__main__":
    print("Getting Ontology and training...")
    if os.path.exists("./SemEval2007/training.json"):
        ontology = Ontology(filepath="./SemEval2007/ontology.json")
        training = Document(filepath="./SemEval2007/training.json")
    else:
        ontology, training = buildTraining()
    print("\tComplete.")

    print("Getting testing set...")
    if os.path.exists("./SemEval2007/testing.json"):
        testing = Document(filepath="./SemEval2007/testing.json")
    else:
        testing = buildTesting()
    print("\tComplete.")

    print("Running Relation Extractor...")
    extractor = RelationExtractor(ontology=ontology)

    print("\tFitting extractor...")
    extractor.fit(training)
    print("\t\tComplete.")

    print("\tPredicting with extractor...")
    extractor.predict(testing)
    print("\t\tComplete.")

    corpus, _ = score(ontology, testing)

    print(corpus)