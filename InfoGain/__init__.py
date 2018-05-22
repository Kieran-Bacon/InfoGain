# Ontology design and interaction
from .Ontology import Ontology
from .Concept import Concept
from .Relation import Relation
from .Fact import Fact

# Information Extraction
from .RelationExtractor import RelationExtractor

# Inference
from .ReasoningEngine import ReasoningEngine

# Documents
from .Documents.Datapoint import Datapoint
from .Documents.Document import Document
from .Documents.TrainingDocument import TrainingDocument

import logging
logging.basicConfig(format='%(asctime)s|%(levelname)s|%(message)s', datefmt='%m/%d/%Y %I:%M:%S')