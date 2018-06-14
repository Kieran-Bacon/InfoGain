import os

from .Language import DomainResources as Language 
from .Medicine import DomainResources as Medicine

ROOT = os.path.dirname(os.path.realpath(__file__))
TEXT_COLLECTIONS = [os.path.join(ROOT,"TextCollections", name) for name in os.listdir(os.path.join(ROOT,"TextCollections"))]
DICTIONARY = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Dictionary.txt")

class TEXT(object):
    def __init__(self):
        self.files = [os.path.join(ROOT,"TextCollections", name) for name in os.listdir(os.path.join(ROOT,"TextCollections"))]
 
    def __iter__(self):
        for fname in self.files:
            for line in open(fname):
                yield line.split()

def hasEmbedder():
    return os.path.exists(os.path.join(ROOT,"WikipediaWord2Vec"))
        
def loadEmbedder():
    from gensim.models import Word2Vec
    return Word2Vec.load(os.path.join(ROOT,"WikipediaWord2Vec"))