import os, re, random

from InfoGain.Knowledge import Ontology, Concept, Relation
from InfoGain.Documents import Document, Datapoint, score
from InfoGain.Extraction import RelationExtractor

DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), "Dataset-ADE"))

def buildOntology():
    # Generating ontology
    ADE = Ontology(name="ADE")

    # Add concepts
    ADE.addConcept(Concept("Drug"))
    ADE.addConcept(Concept("Effect"))

    # Add relation
    ADE.addRelation(Relation({"Drug"}, "causes", {"Effect"}))

    ADE.save(folder=DATA, filename="ADE.json")
    return ADE

def buildPositive(ADE):
    # Open up positive instances
    with open(os.path.join(DATA, "DRUG-AE.rel"), "r") as handler:
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
    ADE.save(folder=DATA)

    positiveDatapoints = Document()
    positiveDatapoints.datapoints(points)
    positiveDatapoints.save(folder=DATA, filename="PositiveData.json")

    return positiveDatapoints

def buildNegative(ADE):
    # Generate Negative set
    with open(os.path.join(DATA, "ADE-NEG.txt"), "r") as handler:
        content = handler.read().splitlines()

    content = "\n".join([" ".join(line.split()[2:]).lower() for line in content])

    negativeDatapoints = Document(content=content)
    negativeDatapoints.processKnowledge(ADE)

    for point in negativeDatapoints.datapoints():
        point.annotation = -1

    negativeDatapoints.save(folder=DATA, filename="NegativeData.json")

    return negativeDatapoints

if __name__ == "__main__":

    print("Get ontology...")
    if os.path.exists(os.path.join(DATA, "ADEontology")):
        ADE = Ontology(filepath=os.path.join(DATA, "ADEontology"))
    else:
        ADE = buildOntology()

    print("Get positive set...")
    if os.path.exists(os.path.abspath(os.path.join(DATA, "PositiveData.json"))):
        positive = Document(filepath=os.path.join(DATA, "PositiveData.json"))
    else:
        positive = buildPositive(ADE)

    print("Get negative set...")
    if os.path.exists(os.path.abspath(os.path.join(DATA, "NegativeData.json"))):
        negative = Document(filepath=os.path.join(DATA, "NegativeData.json"))
    else:
        negative = buildNegative(ADE)

    # Compile and resemble documents
    print("Compile the datapoints")
    posData, negData = positive.datapoints(), negative.datapoints()

    random.shuffle(posData)
    random.shuffle(negData)

    Xtr = posData[:int(len(posData)/2)] + negData[:int(len(negData)/2)]
    Xte = posData[int(len(posData)/2):] + negData[int(len(negData)/2):]

    training, testing = Document(), []
    training.datapoints(Xtr)
    for i in range(0, len(Xte), int(len(Xte)/5)):
        testingDocument = Document()
        testingDocument.datapoints(Xte[i:i + int(len(Xte)/5)])
        testing.append(testingDocument)
    print("\tComplete.")

    print("Running Extractor")
    extractor = RelationExtractor(ontology=ADE)

    print("\tRunning trainer...")
    extractor.fit(training)
    print("\t\tComplete.")

    print("\t Running predict...")
    testing = extractor.predict(testing)
    print("\t\tComplete.")

    # Pretty print the results  
    score(extractor, testing, pprint=True)