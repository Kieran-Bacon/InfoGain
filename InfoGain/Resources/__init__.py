import os
from .Language import Language

ROOT = os.path.dirname(os.path.realpath(__file__))
TEXT_COLLECTIONS = [os.path.join(ROOT,"TextCollections", name) for name in os.listdir(os.path.join(ROOT,"TextCollections"))]
DICTIONARY = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Dictionary.txt")

def hasEmbedder():
    return os.path.exists(os.path.join(ROOT,"Word2VecModel"))
        

def loadEmbedder():
    print("Loadin Embedder")
    from gensim.models import Word2Vec
    return Word2Vec.load(os.path.join(ROOT, "Word2VecModel"))