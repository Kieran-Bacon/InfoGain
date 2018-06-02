class EmptyDocument(Exception): pass
class IncompleteDatapoint(Exception): pass

from .Datapoint import Datapoint
from .Document import Document

def score(ontology, documents: [Document]):

    corpus = {"precision": 0, "recall": 0, "f1": 0}
    scores = {}
    total_datapoint_count = 0 

    for document in documents:
        # Count all datapoints
        total_datapoint_count += len(document.datapoints())

        # Calculate precision
        precision = sum([point.annotation == point.prediction for point in document.datapoints()])/len(document.datapoints())
        corpus["precision"] += precision*len(document.datapoints())

        # Recall 
        tempDoc = Document(content=document.text())
        tempDoc.processKnowledge(ontology)

        newData = set(tempDoc.datapoints())
        allData = set(document.datapoints())

        assert(len(allData) == len(document.datapoints()))

        recall = len(newData.intersection(allData))/len(allData)
        corpus["recall"] += recall*len(document.datapoints())

        # Calculate F1

        f1 = (2*(precision*recall))/(precision+recall) if precision+recall else 0
        corpus["f1"] += f1*len(document.datapoints())

        scores[document] = {"precision": precision, "recall": recall, "f1": f1}

    for k, v in corpus.items():
        corpus[k] = v/total_datapoint_count

    return corpus, scores

def annotate(ontology, documents: [Document]):
    """ Annotate some documents! """

    from .DocumentOperations import cmdread

    for document in documents:

        # Check to see if the document is to be saved
        ans = cmdread("Save the generated training document?", ['Y','N'])
        filename = cmdread("Filename: ") if ans == "Y" else None

        # Process the document according to the ontology
        document.processKnowledge(ontology)

        index, total = 0, len(document.datapoints())
        annotated = []

        for point in document.datapoints():

            index += 1
            mult = int((index/total)*25)

            print("|" + "#"*mult + "-"*(25-mult) + "|", "({}/{} datapoints)".format(index, total))

            print("TEXT:\n{}\n".format(point.text))

            print("RELATION: {}  {}   {}  {}   {}".format(point.domain["concept"], point.domain["text"], point.relation, point.target["concept"], point.target["text"]))

            ans = cmdread("Does this string represent this relation?",['-1','0','1'])

            point.annotation = int(ans)
            annotated.append(point)

            print("\n\n\n\n")

        xtr = Document(name=filename, content=document.text())
        xtr.datapoints(annotated)
        
        if filename: xtr.save(filename=filename)

        return xtr