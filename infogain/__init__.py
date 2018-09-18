import logging

gensim = logging.getLogger("gensim")
gensim.setLevel(logging.ERROR)

from . import knowledge
from . import artefact
from . import extraction
from . import cognition
from . import resources