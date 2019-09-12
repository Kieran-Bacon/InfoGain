class EmptyDocument(Exception): pass
class IncompleteDatapoint(Exception): pass

from .entity import Entity
from .annotation import Annotation
from .document import Document


def score(ontology, documents: [Document], pprint: bool=False)->(dict, dict):
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
        print (bool) - A toggle to allow the output to be printed nicely to the screen

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
        if not len(document.datapoints()): continue

        # Count all datapoints
        total_datapoint_count += len(document.datapoints())

        # Calculate precision
        precision = sum([point.annotation == point.prediction for point in document.datapoints()])/len(document.datapoints())
        corpus["precision"] += precision*len(document.datapoints())

        # Recall
        tempDoc = Document(content=document.text())
        tempDoc.processKnowledge(ontology)

        originalPoints, newPoints = set(document.datapoints()), set(tempDoc.datapoints())

        recall = float(len(newPoints.intersection(originalPoints)))/len(originalPoints)
        corpus["recall"] += recall*len(document.datapoints())

        # Calculate F1
        f1 = (2*(precision*recall))/(precision+recall) if precision+recall else 0
        corpus["f1"] += f1*len(document.datapoints())

        scores[document] = {"precision": precision, "recall": recall, "f1": f1}

    if not total_datapoint_count: return corpus, scores # The documents provided don't have any datapoints
    for k, v in corpus.items():
        corpus[k] = v/total_datapoint_count

    if pprint:
        print("\n")
        print("="*60, "\n| Extractor scores | Precision  |   Recall   |      F1     |\n", "="*60, sep="")
        print(" "*19, "| {:.8f} | {:.8f} |  {:.8f} |\n".format(corpus["precision"], corpus["recall"], corpus["f1"] ), " "*19, "="*41, sep="")
        print()

        size = max( [len("Document name")] + [len(doc.name) for doc in documents]) + 2

        def calSize(word: str):
            prebuffer = int( round( ((size - len(word))/2) ) )
            postbuffer = (size - len(word)) - prebuffer
            return prebuffer, postbuffer

        pre, pos = calSize("Document name")
        print(" "*pre, "Document name", " "*pos, "| Precision  |   Recall   |     F1", sep="")
        print("-"*(size + 39))
        for doc in documents:

            pre, pos = calSize(doc.name)
            print(
                " "*pre,
                doc.name,
                " "*pos,
                "| {:.8f} | {:.8f} | {:.8f}".format(scores[doc]["precision"], scores[doc]["recall"], scores[doc]["f1"]),
                sep=""
            )

        print("\n\n")

    return corpus, scores