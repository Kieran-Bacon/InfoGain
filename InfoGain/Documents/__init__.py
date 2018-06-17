class EmptyDocument(Exception): pass
class IncompleteDatapoint(Exception): pass

from .Document import Document
from .Datapoint import Datapoint

def score(ontology, documents: [Document])->(dict, dict):
    """ Calculate the precision, recall and F1 score for a collection of documents.
    The datapoints within the document are used to perform the scoring. The precision is
    calculated from the datapoints correctly returned in recall. A comparison is made between
    the annotation of the datapoint and its prediction.
    Recall is determined by processing the text of the datapoints using the ontology provided.
    The F1 score is an equation of the two other scores.

    Handles a single document or a collection

    Params:
        ontology (Ontology) - An ontology of concepts and relations to direct processing
        documents ([Document]) - A collection of document objects to score.

    Returns:
        corpus scores (dict) - A dictionary where the keys are the metrics, and the 
            value is the collection averages
        document scores (dict) -  A dictionary where the keys are the documents, and 
            the values are a dictionary of the metric values for that document
    """

    if not isinstance(documents, list):
        documents = [documents]

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

        originalPoints, newPoints = set(document.datapoints()), set(tempDoc.datapoints())

        print("New")
        for point in newPoints:
            print(point, "-", "***"+point.text+"***", point in originalPoints)

        print("Original")
        for point in originalPoints:
            print(point, "-", "***"+point.text+"***", point in newPoints)

        print(sum([1 for i in newPoints if i in originalPoints]))
        assert( sum([1 for i in newPoints if i in originalPoints]) == len(newPoints.intersection(originalPoints)))


        recall = float(len(newPoints.intersection(originalPoints)))/len(originalPoints)
        print(float(len(newPoints.intersection(originalPoints))))
        print(len(originalPoints))
        print(recall)
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

    if not isinstance(documents, list):
        documents = [documents]

    def cmdread(msg: str, valid: list = None):
        """ Read input from the command line ensuring that the input is valid """
        from builtins import input

        if valid:
            msg += " ("+",".join(valid)+")"

        msg = "="*(len(msg)+2) + "\n|" + msg + "|\n" + "="*(len(msg)+2) + "\n"

        while True:
            read = input(msg + "\n")
            if valid is None or read in valid: return read
            else: print("Invalid input.")

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