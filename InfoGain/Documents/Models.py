class SpellingModel:
    """ Singleton class for the correction of words present within text """

    WORDS = None
    size = 0

    @classmethod
    def load(cls):
        if cls.WORDS is None:
            # Import the counter data type
            import re
            from .Document import Document
            from collections import Counter

            from .. import Resources

            def words(text):
                return re.findall("\w+", text.lower())

            cls.WORDS = Counter(words(open(Resources.DICTIONARY).read()))

            documents = [Document(filepath=path) for path in Resources.TEXT_COLLECTIONS]
            for document in documents:
                words = [word for sentence in document.words() for word in sentence]
                cls.WORDS.update(words)

            cls.size = sum(cls.WORDS.values())

    @classmethod
    def train(cls, words: [str]):
        cls.load()
        cls.WORDS.update(words)
        cls.size = sum(cls.WORDS.values())

    @classmethod
    def predict(cls, word: str):
        """ Predict the correct spelling of a word """
        cls.load()
        return max(cls._candiates(word), key=cls._probabilites)

    @classmethod
    def _candiates(cls, word: str):
        return (cls._known([word]) or cls._known(cls._edits1(word)) or cls._known(cls._edits2(word)) or [word])

    @classmethod
    def _known(cls, words):
        return set(w for w in words if w in cls.WORDS)

    @classmethod
    def _probabilites(cls, word):
        return cls.WORDS[word] / cls.size

    @classmethod
    def _edits1(cls, word):
        "All edits that are one edit away from `word`."
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    @classmethod
    def _edits2(cls, word): 
        "All edits that are two edits away from `word`."
        return (e2 for e1 in cls._edits1(word) for e2 in cls._edits1(e1))