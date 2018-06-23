class SpellingModel:
    """ Singleton class for the correction of words present within text """

    size = 0
    WORDS = None

    @classmethod
    def load(cls, filepath: str = None) -> None:
        """ Initialise the singleton class if the class hasn't already been initialized 

        Params:
            filepath (str) - path to a saved version of the spelling model
        """

        if cls.WORDS is None:

            if filepath:
                import pickle

                with open(filepath, "rb") as handler:
                    data = pickle.load(handler)
                    cls.size = data["size"]
                    cls.WORDS = data["WORDS"]
            
            else:
 
                # Import the counter data type
                import re
                from ...Documents import Document
                from collections import Counter

                from ... import Resources

                def words(text):
                    return re.findall(r"\w+", text.lower())

                cls.WORDS = Counter(words(open(Resources.DICTIONARY).read()))

                documents = [Document(filepath=path) for path in Resources.TEXT_COLLECTIONS]
                for document in documents:
                    words = [word for sentence in document.words() for word in sentence]
                    cls.WORDS.update(words)

                cls.size = sum(cls.WORDS.values())

    @classmethod
    def save(cls, folder: str = "./", filename: str = "SpellingModel.txt") -> None:
        """ Save the spelling model to be able to recall later

        Params:
            folder (str) - The directory where the model is going to be saved
            filename (str) - The name given to spelling model once saved
        """
        if cls.WORDS is None: return

        import os, pickle
        with open(os.path.join(folder, filename), "wb") as handler:
            pickle.dump({"size": cls.size, "WORDS": cls.WORDS}, handler, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def train(cls, words: [str]) -> None:
        """ Train the spelling model using a collection of words.

        Params: 
            words ([str]) - The collection of words
        """
        cls.load()
        cls.WORDS.update(words)
        cls.size = sum(cls.WORDS.values())

    @classmethod
    def predict(cls, word: str) -> str:
        """ Predict the correct spelling of a word 
        
        Params:
            word (str) - The word to predict the correct spelling of

        Returns:
            str - The word the spelling model predicted for the word
        """
        cls.load()
        return max(cls._candiates(word), key=cls._probabilites)

    @classmethod
    def _candiates(cls, word: str) -> {str}:
        """ Collect the candidate words to replace the provided word

        Params:
            word (str) - The word to find the candidates for

        Returns:
            {str} - The collection of candidate solutions for the provided word
        """
        return (cls._known([word]) or cls._known(cls._edits1(word)) or cls._known(cls._edits2(word)) or [word])

    @classmethod
    def _known(cls, words: [str]) -> {str}:
        """ Minimise the collection of words into a set of words known to the model

        Params:
            words ([str]) - The collection of words to minimise

        Returns:
            {str} - A minimized collection of words
        """
        return set(w for w in words if w in cls.WORDS)

    @classmethod
    def _probabilites(cls, word: str) -> float:
        """ Return the probability that a word would appear in text 
        
        Params:
            word (str) - The word to find the probability

        Returns:
            float - The probability of the provided word is found within text
        """
        return cls.WORDS[word] / cls.size

    @classmethod
    def _edits1(cls, word: str) -> {str}:
        """ Return the set of words that are one edit away from the provided words.
        
        Params:
            word (str) - The word to edit
        
        Returns:
            {str} - A collection of strings that is a single character changes away from the
                original word
        """
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    @classmethod
    def _edits2(cls, word: str) -> {str}: 
        """ Return the set of words that is two edits away from the originally provided word
        
        Params:
            word (str) - The word to edit
        
        Returns:
            {str} - A collection of strings that is two character changes away from the
                original word
        """
        return (e2 for e1 in cls._edits1(word) for e2 in cls._edits1(e1))