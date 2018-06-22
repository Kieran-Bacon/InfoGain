from ... import Resources

import logging, numpy, math
from gensim.models import Word2Vec

class Embedder:

    def __init__(self, word_embedding_model: Word2Vec = None, embedding_size: int = 300, count: int = 10, workers: int = 4):

        if word_embedding_model is None:
            if Resources.hasEmbedder():
                self.model = Resources.loadEmbedder()
            else:
                self.model = Word2Vec(Resources.TEXT(), size=embedding_size, min_count=count, workers=workers)
        else:
            self.model = word_embedding_model

    def train(self, sentences: [[str]]) -> None:
        self.model.build_vocab(sentences, update=True)
        self.model.train(sentences, total_examples=len(sentences), epochs=self.model.epochs)

    def size(self):
        return self.model.layer1_size

    def workers(self):
        return self.model.workers

    def word(self, word: str):
        if not word in self.model.wv:
            logging.warning("Vocabulary missing during sentence embedding: '"+ word +"'")
            return numpy.zeros(self.size())
        return self.model.wv[word]
        

    def sentence(self, sentence: str) -> numpy.array:
        """ Convert a sentence of variable length into a sentence embedding using the learn word
        embeddings """

        embedding = numpy.zeros(self.size())
        words = sentence.split()

        def pf(index: int, alpha: float = 1, beta: float = 0) -> float:
            """ Return the output of a monotonic function as to include order information into
            the word embeddings """
            # TODO: Change function to something meaningful with support from someone
            #return alpha*(math.e**index) + beta
            return 1
            return -numpy.log((index+1)/(len(words)+1))

        for index, word in enumerate(words):
            
            embedding += pf(index)*self.word(word)
                
        return embedding if not len(words) else embedding/len(words)
