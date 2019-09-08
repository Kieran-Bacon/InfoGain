import logging

for module in ["infogain.knowledge", "gensim"]:
    logger = logging.getLogger(module)
    logger.setLevel(logging.ERROR)

from . import knowledge
from . import artefact
from . import extraction
from . import cognition
from . import resources
from .serialisers import SerialiserFactory as Serialiser