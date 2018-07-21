from InfoGain.Extraction import RelationExtractor
from InfoGain.Documents import Document
from InfoGain.Resources import Language, Calibrator

import matplotlib.pyplot as plt

training_points = [point for doc in Language.training() for point in doc.datapoints()]
results, structures, alphas = Calibrator.tune(RelationExtractor, Language.ontology(), training_points)