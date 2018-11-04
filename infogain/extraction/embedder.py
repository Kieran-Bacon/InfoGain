from .. import resources

import logging, numpy, math
from gensim.models import Word2Vec

log = logging.getLogger(__name__)

class Embedder:
    """ Embeds words and sentences into a vector of real values.

    Params:
        word_embedding_model (Word2Vec) - A word to vector model already made and generated
        embedding_size (int) - The size of the embedded vectors
        count (int) - The number of times a word needs to be seen before an embedding is made
        workers (int) - The number of processes to be used to help train the model
    """ 

    def __init__(self,
        word_embedding_model: Word2Vec = None,
        embedding_size: int = 300,
        count: int = 10,
        workers: int = 4):

        if word_embedding_model is None:
            if resources.hasEmbedder():
                self.model = resources.loadEmbedder()
            else:
                self.model = Word2Vec(resources.TEXT(), size=embedding_size, min_count=count, workers=workers)
        else:
            self.model = word_embedding_model

    def train(self, sentences: [[str]]) -> None:
        """ Train the model on a collection of sentences

        Params:
            sentences ([[str]]) - A collection of sentences broken down into a list of words.
                Words are kept in order in a sentence to train semantics.
        """
        self.model.build_vocab(sentences, update=True)
        self.model.train(sentences, total_examples=len(sentences), epochs=self.model.epochs)

    def size(self) -> int:
        """ Return the size of the embedding vectors """
        return self.model.trainables.layer1_size

    def workers(self) -> int:
        """ Return the number of works being used by the embedding method """
        return self.model.workers

    def word(self, word: str) -> numpy.array:
        """ Embed the provided word and return the real value vector that represents it

        Params:
            word (str) - The word to be embedded

        Returns:
            vector (numpy.array) - The embedded vector that represents the word
        """
        if word not in self.model.wv:
            log.warning("Unrecognised word: {}".format(word))
            return numpy.zeros(self.size())
        return self.model.wv[word]
        

    def sentence(self, sentence: str) -> numpy.array:
        """ Convert a sentence of variable length into a sentence embedding using the learn word
        embeddings within the model.
        
        Params:
            sentence (str) - A single string that represents a single sentence
            missed (bool) - Toggle to return missed words during embedding
        
        Returns:
            vector (numpy.array) - A vector representation of the of the sentence
        """

        embedding = numpy.zeros(self.size())  # Sentence embedding
        words = sentence.split()  # Words of the sentence

        def pf(index: int, alpha: float = 1, beta: float = 0) -> float:
            """ Return the output of a monotonic function as to include order information into
            the word embeddings.
            
            Params:
                index (int) - The index of the word within the sentence
                alpha (float) - A parameter to affect the magnitude of the result
                beta (float) - A secondary parameter to affect the magnitude of the result
            """
            return 1

        # Embedd the words of the sentence
        for index, word in enumerate(words): embedding += pf(index)*self.word(word)

        if len(words): embedding = embedding/len(words)
        return embedding