import os, re, random

from InfoGain.Knowledge import Ontology, Concept, Relation
from InfoGain.Documents import Document, Datapoint, score
from InfoGain.Extraction import RelationExtractor

def buildOntology():
    # Generating ontology
    ADE = Ontology(name="ADE")

    # Add concepts
    ADE.addConcept(Concept("Drug"))
    ADE.addConcept(Concept("Effect"))

    # Add relation
    ADE.addRelation(Relation({"Drug"}, "causes", {"Effect"}))

    ADE.save(folder="./ADE_Dataset", filename="ADE.json")
    return ADE

def buildPositive(ADE):
    # Open up positive instances
    with open("./ADE_Dataset/DRUG-AE.rel", "r") as handler:
        content = handler.read().splitlines()

    domains, targets, points = set(), set(), []
    for line in content:
        line = line.split("|")

        sentence = line[1].lower()
        domain = line[5].lower()
        target = line[2].lower()

        domains.add(domain)
        targets.add(target)

        domain_span = re.search(re.escape(domain),sentence).span()
        target_span = re.search(re.escape(target),sentence).span()

        first = domain_span if int(domain_span[0]) < int(target_span[0]) else target_span
        second = domain_span if int(domain_span[0]) > int(target_span[0]) else target_span

        content = {}
        content["text"] = sentence
        content["domain"] = {"concept":"Drug", "text":domain}
        content["target"] = {"concept":"Effect", "text":target}
        content["context"] = {"left":sentence[:int(first[0])],\
                                "middle":sentence[int(first[1]):int(second[0])],\
                                "right":sentence[int(second[1]):]}

        content["relation"] = "causes"
        content["annotation"] = 1

        points.append(Datapoint(content))

    [ADE.concept("Drug").alias.add(r) for r in domains]
    [ADE.concept("Effect").alias.add(r) for r in targets]
    ADE.save(folder="./ADE_Dataset")

    positiveDatapoints = Document()
    positiveDatapoints.datapoints(points)
    positiveDatapoints.save(folder="./ADE_Dataset", filename="PositiveData.json")

    return positiveDatapoints

def buildNegative(ADE):
    # Generate Negative set
    with open("./ADE_Dataset/ADE-NEG.txt", "r") as handler:
        content = handler.read().splitlines()

    content = "\n".join([" ".join(line.split()[2:]).lower() for line in content])

    negativeDatapoints = Document(content=content)
    negativeDatapoints.processKnowledge(ADE)

    for point in negativeDatapoints.datapoints():
        point.annotation = -1

    negativeDatapoints.save(folder="./ADE_Dataset", filename="NegativeData.json")

    return negativeDatapoints

if __name__ == "__main__":

    print("Get ontology...")
    if os.path.exists("./ADE_Dataset/ADEontology"):
        ADE = Ontology(filepath="./ADE_Dataset/ADEontology")
    else:
        ADE = buildOntology()

    print("Get positive set...")
    if os.path.exists(os.path.abspath("./ADE_Dataset/PositiveData.json")):
        positive = Document(filepath="./ADE_Dataset/PositiveData.json")
    else:
        positive = buildPositive(ADE)

    print("Get negative set...")
    if os.path.exists(os.path.abspath("./ADE_Dataset/NegativeData.json")):
        negative = Document(filepath="./ADE_Dataset/NegativeData.json")
    else:
        negative = buildNegative(ADE)

    # Compile and resemble documents
    print("Compile the datapoints")
    posData, negData = positive.datapoints(), negative.datapoints()

    random.shuffle(posData)
    random.shuffle(negData)

    Xtr = posData[:int(len(posData)/2)] + negData[:int(len(negData)/2)]
    Xte = posData[int(len(posData)/2):] + negData[int(len(negData)/2):]

    training, testing = Document(), Document()
    training.datapoints(Xtr)
    testing.datapoints(Xte)
    print("\tComplete.")

    print("Running Extractor")
    extractor = RelationExtractor(ontology=ADE)

    print("\tRunning trainer...")
    extractor.fit(training)
    print("\t\tComplete.")

    print("\t Running predict...")
    extractor.predict(testing)
    print("\t\tComplete.")


    corpus, documents = score(extractor, testing)
    print("Scores:")
    print(corpus)
    print(documents)