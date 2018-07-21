from numpy import *
from sklearn.model_selection import KFold
from gensim.models import Word2Vec
import logging

from ...Knowledge import Ontology
from ...Documents import Datapoint, Document, score
from ...Extraction import RelationExtractor

from multiprocessing import Process, Queue

def RETune(ont: Ontology, training: [Datapoint]):
    """ Tune the relation extraction class over a range of various values and return the correct
    parameters

    Params:
        ont (RelationExtractor/Ontology) - The ontology of information needed to form the base
        training ([Datapoint]) - A collection of data points to be able to perform cross
            validation

    Returns:
        scores - A data structure that holds all of the metric scores for the extractor against
            the structures then against the alphas
        structures - The network sizes and shapes
        alphas - The neural network 
    """

    logging.getLogger().setLevel(logging.ERROR)  # Ensure that logging output is captured

    # The structures to validate
    structures = [(3,1), (4,2), (6,3), (8,4), (12,6), (20,10), (50,20)]
    alphas = logspace(-16,1,20)

    scores = []
    for layers in structures:
        layer_scores = []
        for alpha in alphas:
            def run(queue, tr, val):
                tr, val = [training[i] for i in tr], [training[i] for i in val]

                # Create a new extractor model
                ext = RelationExtractor(ontology=ont, hidden_layers=layers, alpha=alpha)

                # Generate the training and validation documents
                Xtr, Xtv = Document(), Document()
                Xtr.datapoints(tr)
                Xtv.datapoints(val)

                # Fit, predict and score
                ext.fit(Xtr)
                ext.predict(Xtv)

                results = score(ont, [Xtv])

                queue.put(results[0])

            queue = Queue()
            processors = [Process(target=run, args=(queue, tr, val)) for tr, val in KFold(n_splits=5, shuffle=True).split(training)]
            [p.start() for p in processors]
            [p.join() for p in processors]

            alpha_scores = [queue.get() for _ in range(5)]

            compressed = {"precision":[],"recall":[],"f1":[]}
            for r in alpha_scores:
                for k, v in r.items():
                    compressed[k].append(v)
            
            for k, v in compressed.items():
                compressed[k] = sum(v)/len(v)

            layer_scores.append(compressed)
        scores.append(layer_scores)

    return scores, structures, alphas