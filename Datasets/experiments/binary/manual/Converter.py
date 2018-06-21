import re
from InfoGain import Ontology, Document, TrainingDocument, Datapoint, Concept, Relation

import os
from os import listdir

ont = Ontology()
xtr = TrainingDocument()

concepts = {}
relations = {}

textFormat = ["domain", "relation", "target", "reltext", "text"]

relmap = {
    "sues": "sued",
    "is_acquiring": "acquired",
    "to_acquire": "acquired",
    "to_buy": "buy",
    "was_born": "born"
}

def cleanrelation(string):
    string = re.sub("'\w", "", string)
    string = re.sub("\s", "_", string.strip())
    string = string.lower()

    a = string.split("_")
    if len(a) == 2 and a[0] == a[1]:
        string = a[0]

    return relmap.get(string,string)

for folder in ["./dev", "./test"]:
    for files in listdir(folder):
        with open(os.path.join(folder, files)) as filehandler:

            for _ in range(2):
                dp = filehandler.readline()

            while dp:

                dp = {k: v for k, v in zip(textFormat, filehandler.readline().split("\t"))}

                if "reltext" in dp and not "text" in dp: dp["text"] = dp["reltext"]
                if not all([x in dp.keys() for x in textFormat]): break
                if dp["relation"] == "---": continue
                if len(dp["relation"].split()) > 2: continue

                try:
                    float(dp["text"])
                    dp["text"] = dp["reltext"]
                except:
                    pass

                dp["relation"] = cleanrelation(dp["relation"])
                dp["text"] = re.sub("--->|<---|{{{|}}}|\n", "", dp["text"])
                dp["text"] = re.sub("\s", " ", dp["text"])
                text = dp["text"]
                
                conceptOrder = []
                spans = []

                point = Datapoint()

                count = 0
                for match in re.finditer("(?!\[\[\[)[A-Za-z]+ [A-Za-z0-9 \.,&!'\-_]+(?=\]\]\])", dp["text"]):
                    count += 1

                    concept, textrepr = match.group(0)[:match.group(0).index(" ")], match.group(0)[match.group(0).index(" ")+1:]

                    if textrepr == dp["domain"]:

                        domain = concepts.get(concept, Concept(concept))
                        domain.addRepr(textrepr)
                        concepts[concept] = domain
                        
                        point.setDomain(concept, textrepr)
                    
                    if textrepr == dp["target"]:

                        target = concepts.get(concept, Concept(concept))
                        target.addRepr(textrepr)
                        concepts[concept] = target

                        point.setTarget(concept, textrepr)

                    conceptOrder.append(textrepr)
                    spans.append(match.span())

                try:
                    left = dp["text"][:spans[0][0]-3]
                    middle = dp["text"][spans[0][1]+3:spans[1][0]-3]
                    right = dp["text"][spans[1][1]+3:]
                    text = " ".join([left, conceptOrder[0], middle, conceptOrder[1], right])

                    point.setRelation(dp["relation"])
                    point.setText(text)
                    point.setContext(left.strip(), middle.strip(), right.strip())
                    point.annotation = True

                    try:
                        point.target
                        xtr.addDatapoint(point)
                    except:
                        pass
                except:
                    pass



if False and os.path.exists("./datasetont.json"):
    ont = Ontology(filepath="./datasetont.json")
else:
    # Count the relations
    relCount = {}
    for point in xtr.datapoints():
        relCount[point.relation] = relCount.get(point.relation, 0) + 1

    # Build the relations objects
    relations = {k: Relation(set(),k,set()) for k, v in relCount.items() if v >= 10}

    # Remove
    points_to_remove = []
    for point in xtr.datapoints():
        if not point.relation in relations:
            points_to_remove.append(point)
            continue

        relations[point.relation].domains(concepts[point.domain])
        relations[point.relation].targets(concepts[point.target])

    [xtr.removeDatapoint(p) for p in points_to_remove]

    ont = Ontology()
    [ont.addConcept(con) for con in concepts.values()]
    [ont.addRelation(rel) for rel in relations.values()]
    ont.save("./datasetont.json")



xtr.save("./","xtr.json")
exit()