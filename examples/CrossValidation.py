from InfoGain.Resources import Language
from InfoGain.Extraction import Calibrator, RelationExtractor
from InfoGain.Documents import Document

import random

import matplotlib.pyplot as plt

training_points = [point for doc in Language.training() for point in doc.datapoints()]
results, structures, alphas = Calibrator.cross_validation(Language.ontology(), training_points)

print(results)

exit()


struct_i, alpha_i, precision = 0, 0, 0

# Iterate through information to identify best score
for i, result_dict in enumerate(results):
    collection = [d["precision"] for d in result_dict]
    if max(collection) > precision:
        alpha_i, struct_i = collection.index(max(collection)), i
        precision = max(collection)

random.shuffle(training_points)

Xtr, Xte = training_points[:int(len(training_points)/2)], training_points[int(len(training_points)/2):]

# Test set results
XtrDoc = TrainingDocument(datapoints=Xtr)
XteDoc = Document(datapoints=Xte)

ext = RelationExtractor(ontology=Language.ontology())

ext.fit(XtrDoc)
ext.predict(XteDoc)

with open("CalibrationResults.txt", "w") as handler:
    handler.write(str(results))

metrics = {
    "precision": XteDoc.precision(),
    "recall": XteDoc.recall(Language.ontology()),
    "f1": XteDoc.F1(Language.ontology())
}

with open("otherstuff.txt", "w") as handler:
    handler.write(str(results))
    handler.write("\n")
    handler.write("Best Structure:" + str(struct_i))
    handler.write("Best Alpha:" + str(alpha_i))
    handler.write("Xte metrics:" + str(metrics))

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

print(results)

exit()

# Store the values and variance of the two testing aspect
splitValues.append([ x[split] for x in depthScore] )
splitVariance.append([ x[split] for x in depthVariance])
sampleValues.append(depthScore[sample])
sampleVariance.append(depthVariance[sample])

# Plot the findings
figure()
subplot(221)
title("Affect of split on error")
for i, collection in enumerate(splitValues):
    plot(minSplit, collection, colour[i], label="D" + str(treeDepth[i]))
    
subplot(222)
title("Split value variance")
for i, collection in enumerate(splitVariance):
    plot(minSplit, collection, colour[i], label="Depth " + str(treeDepth[i]))
    
    
figure()
subplot(221)
title("Affect of sample on error")
for i, collection in enumerate(sampleValues):
    plot(minSample, collection, colour[i], label="Depth " + str(treeDepth[i]))
    
subplot(222)
title("Sample value variance")
for i, collection in enumerate(sampleVariance):
    plot(minSample, collection, colour[i], label="Depth " + str(treeDepth[i]))

with open("./results.txt", "w") as handler:
    handler.write(str(a))