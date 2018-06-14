import re, json

from InfoGain.Knowledge import Ontology, Concept, Relation
from InfoGain.Documents import Document, Datapoint, score
from InfoGain.Extraction import RelationExtractor

import matplotlib.pyplot as plt

if False:
    # Generating ontology
     
    ADE = Ontology()

    Drug, Effect = Concept("Drug"), Concept("Effect")
    Causes = Relation({Drug}, "causes", {Effect})

    ADE.addConcept(Drug)
    ADE.addConcept(Effect)
    ADE.addRelation(Causes)

    domains, targets = set(), set()

    points = []

    with open("./DRUG-AE.rel", "r") as handler:

        content = handler.read().splitlines()

    for line in content:
        line = line.split("|")

        sentence = line[1].lower()
        domain = line[5].lower()
        target = line[2].lower()

        domains.add(domain)
        targets.add(target)

        if re.search(re.escape(domain),sentence) is None: print(line)
        if re.search(re.escape(target),sentence) is None: print(line)

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

    [Drug.alias.add(r) for r in domains]
    [Effect.alias.add(r) for r in targets]

    ADE.save(filename="ADE_Ontology.json")

    adverseEffects = Document()
    adverseEffects.datapoints(points)
    adverseEffects.save(filename="PositiveSet.json")

if False:
    # Produce Negative data set

    ADE_Ontology = Ontology(filepath="./ADE_Ontology.json")

    with open("./ADE-NEG.txt", "r") as handler:
        content = handler.read().splitlines()

    number_of_negative_points = len(content)

    raw_document = []
    for line in content:
        raw_document.append(" ".join(line.split()[2:]).lower())

    with open("rawNegative.txt", "w") as handler:
        handler.write("\n".join(raw_document))

    negativeDatapoints = Document(filepath="rawNegative.txt")
    negativeDatapoints.processKnowledge(ADE_Ontology)

    print(len(negativeDatapoints)/number_of_negative_points)

    for point in negativeDatapoints.datapoints():
        point.annotation = -1

    negativeDatapoints.save(filename="NegativeSet.json")

if False:
    with open("./ADE-NEG.txt", "r") as handler:
        content = handler.read().splitlines()

    number_of_negative_points = len(content)

    negative = Document(filepath="./NegativeSet.json")

    with open("./comparison.txt", "w") as handler:
        handler.write(negative.text())

    print("Recall", len(negative)/number_of_negative_points)

# Running the extractor
if True:

    positive = Document(filepath="./PositiveSet.json")
    negative = Document(filepath="./NegativeSet.json")
    posData, negData = [p for p in positive.datapoints()], [p for p in negative.datapoints()]

    import random
    random.shuffle(posData)
    random.shuffle(negData)

    Xtr = posData[:int(len(posData)/2)] + negData[:int(len(negData)/2)]
    Xte = posData[int(len(posData)/2):] + negData[int(len(negData)/2):]

    training, testing = Document(), Document()
    training.datapoints(Xtr)
    testing.datapoints(Xte)

    ext = RelationExtractor(filepath="./ADE_Ontology.json")

    ext.fit(training)

    predicted = ext.predict(testing)

    corpus, documents = score(ext, predicted)

    print("Corpus precision score is:", corpus["precision"])


if False:
    random.shuffle(posData)
    random.shuffle(negData)

    Xtr = posData[:int(len(posData)/2)] + negData[:int(len(negData)/2)]
    Xte = posData[int(len(posData)/2):] + negData[int(len(negData)/2):]
    
    results, structures, alphas = Calibrator.cross_validation(ont, Xtr)

    struct_i, alpha_i, precision = 0, 0, 0

    # Iterate through information to identify best score
    for i, result_dict in enumerate(results):
        collection = [d["precision"] for d in result_dict]
        if max(collection) > precision:
            alpha_i, struct_i = collection.index(max(collection)), i
            precision = max(collection)

    # Test set results
    XtrDoc = TrainingDocument(datapoints=Xtr)
    XteDoc = Document(datapoints=Xte)

    ext = RelationExtractor(ontology=ont)

    ext.fit(XtrDoc)
    ext.predict(XteDoc)

    with open("CalibrationResults.txt", "w") as handler:
        handler.write(str(results))

    metrics = {
        "precision": XteDoc.precision()
    }

    with open("otherstuff.txt", "w") as handler:
        handler.write("Best Structure:" + str(struct_i)+"\n")
        handler.write("Best Alpha:" + str(alpha_i)+"\n")
        handler.write("Xte metrics:" + str(metrics)+"\n")

    plt.figure()
    plt.title("Model metrics with changing hidden layers structure")

    struc_range = range(len(structures))
    precision = [results[i][alpha_i]["precision"] for i in struc_range]
    recall = [results[i][alpha_i]["recall"] for i in struc_range]
    f1 = [results[i][alpha_i]["F1"] for i in struc_range]

    plt.plot(range(len(structures)), precision, "b", label="Precision")
    plt.plot(range(len(structures)), recall, "g", label="Recall")
    plt.plot(range(len(structures)), f1, "y", label="F1")

    plt.xlabel("Structure ID")

    plt.savefig("./results1.pdf", bbox_inches='tight')

    plt.figure()
    plt.title("Model metrics with changing alphas")

    alpha_range = range(len(alphas))
    precision = [results[struct_i][i]["precision"] for i in alpha_range]
    recall = [results[struct_i][i]["recall"] for i in alpha_range]
    f1 = [results[struct_i][i]["F1"] for i in alpha_range]

    plt.plot(alpha_range, precision, "b", label="Precision")
    plt.plot(alpha_range, recall, "g", label="Recall")
    plt.plot(alpha_range, f1, "y", label="F1")

    plt.xscale("log")
    plt.xlabel("Alpha value")

    plt.savefig("./results2.pdf", bbox_inches='tight')



