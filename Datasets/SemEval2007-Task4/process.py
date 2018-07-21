import os, re

from InfoGain.Knowledge import Ontology, Concept, Relation
from InfoGain.Documents import Document, Datapoint, score
from InfoGain.Extraction import RelationExtractor, Calibrator

import matplotlib.pyplot as plt

def process_section(sentence):

    try:
        text, info = sentence.split("\n")[:2]
    except:
        print(sentence)
        exit()

    text = text[5:-1]

    e1 = re.search("<e1>.+</e1>", text)


    if e1 is None:
        print(text)
    span1 = e1.span()
    e1 = e1.group(0)[4:-5]

    e2 = re.search("<e2>.+</e2>", text)
    span2 = e2.span()
    e2 = e2.group(0)[4:-5]

    (first, second) = (span1, span2) if span1[0] < span2[0] else (span2, span1)

    left, middle, right = text[:first[0]], text[first[1]:second[0]], text[second[1]:]

    text = re.sub("<[/]*\w\d>", "", text)

    info = re.findall('[\w-]+\(.+?[^)]+\) = ".+?"', info)[-1]
    relation, order, value = re.findall('[\w-]+(?=\()|\(.+?\)|".+?"', info)

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

# Build/Load database
if False:

    concepts, relations = set(), {}

    #build
    for file in os.listdir("./train"):
        if "processed-training" in file: continue

        print(file)
        with open(os.path.join("./train", file), errors='replace') as handler:

            # Read content
            content = handler.read().split("\n\n")

            for point in content:
                if point == "": continue

                point = process_section(point)
                concepts.add(point["domain"])
                concepts.add(point["target"])

                if not point["relation"] in relations:
                    relations[point["relation"]] = {"domains":[], "targets":[]}

                relations[point["relation"]]["domains"].append(point["domain"])
                relations[point["relation"]]["targets"].append(point["target"])


    ontology = Ontology()

    for concept in concepts:
        ontology.addConcept(Concept(concept))

    for name, info in relations.items():
        domains = [ontology.concept(con) for con in info["domains"]]
        targets = [ontology.concept(con) for con in info["targets"]]
        ontology.addRelation(Relation(set(domains), name, set(targets)))

    ontology.save(filename="ont.json")

else:
    ontology = Ontology(filepath="ont.json")


# Convert the dev files into processable files
if False:
    for file in os.listdir("./train"):
        if "processed-training" in file: continue

        datapoints = []

        with open(os.path.join("./train",file), errors='replace') as handler:

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
        document.save(folder="./train", filename="processed-training"+file)

# Create predicting documents
# Convert the dev files into processable files
if False:

    raw_test_data = os.path.join("./key", "raw-test-data")
    if os.path.exists(raw_test_data):
        os.remove(raw_test_data)

    for file in os.listdir("./key"):
        if "processed-testing" in file: continue

        datapoints = []

        with open(os.path.join("./key",file), errors='replace') as handler:

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

        with open(raw_test_data, "a") as handler:
            for point in datapoints:
                handler.write(point.text)
                handler.write("\n")

        document = Document()
        document.datapoints(datapoints)
        document.save(folder="./key", filename="processed-testing"+file)

# Do some relation prediction
if True:



    ext = RelationExtractor(ontology=ontology)

    training = [Document(filepath=os.path.join("./train", name)) for name in os.listdir("./train") if "processed-training" in name]

    ext.fit(training)

    testing = [Document(filepath=os.path.join("./key", name)) for name in os.listdir("./key") if "processed-testing" in name]

    predicted = ext.predict(testing)

    corpus, documents = score(ontology, predicted)

    print("Corpus Results", corpus)
    index, precision = 0, 0
    for i, doc in enumerate(documents.values()):
        if doc["precision"] > precision:
            precision = doc["precision"]
            index = i
    print("Best document result: document", index, "with precision:", precision )

    results = [corpus] + [doc for doc in documents.values()]
    results = [doc["precision"] for doc in results]
    labels = ["Corpus"] + ["Document {}".format(number) for number in range(len(documents))]

    plt.figure()

    plt.bar(range(len(results)), results, 1/1.5)
    plt.xticks(range(len(results)), labels, rotation='vertical')

    plt.ylabel("Precision Scores")

    plt.show

    plt.savefig("./Precision-Bar-Chart.pdf", bbox_inches='tight')


    #[doc.save(folder="./key", filename="predicted-"+doc.name) for doc in predicted]

# Do the testing
if False:

    training = [Document(filepath=os.path.join("./train", name)) for name in os.listdir("./train") if "processed-training" in name]
    testing = [Document(filepath=os.path.join("./key", name)) for name in os.listdir("./key") if "processed-testing" in name]

    Xtr = [point for doc in training for point in doc.datapoints()]
    Xte = [point for doc in testing for point in doc.datapoints()]

    concepts_in_xtr = set()
    for p in Xtr:
        concepts_in_xtr.add(p.domain["text"])
        concepts_in_xtr.add(p.target["text"])

    concepts_in_xte = set()
    for p in Xte:
        concepts_in_xte.add(p.domain["text"])
        concepts_in_xte.add(p.target["text"])

    print(len(concepts_in_xte.intersection(concepts_in_xtr))/len(concepts_in_xte))

if False:
    
    results, structures, alphas = Calibrator.cross_validation(ontology, Xtr)

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

    ext = RelationExtractor(ontology=ontology)

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








    exit()





















    #predicted = [Document(filepath=os.path.join("./key", name)) for name in os.listdir("./key") if "predicted-" in name]

    correctlyAnnotated, total = 0,0
    recallannotated = 0
    alldatapoints = []

    rawDoc = Document(filepath=raw_test_data)
    rawDatapoints = [point for group in document.datapoints() for point in group]

    for document in predicted:
        for group in document.datapoints():
            for point in group:
                alldatapoints.append(point)
                if point.annotation == point.prediction:
                    correctlyAnnotated += 1

                    for rawpoint in rawDatapoints:
                        if rawpoint.isDuplicate(point):
                            recallannotated += 1

                    if point in rawDatapoints:
                        recallannotated += 0
                total += 1

    

    print(correctlyAnnotated,"/",total)
    print(recallannotated, len(rawDatapoints))



    print("Recall: {}/{} - {}%".format(len(rawDatapoints), len(alldatapoints), (len(rawDatapoints)/len(alldatapoints))*100))

    print(len(alldatapoints))
    print(len(rawDatapoints))







    