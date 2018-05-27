import re

# Document specific definitions
PARAGRAPH = re.compile("[\n\n|\n]")
SENTENCE = re.compile("(?!\w+)[.?!][^\w+]")

def cmdread(msg: str, valid: list = None):
    """ Read input from the command line ensuring that the input is valid """

    if valid:
        msg += " ("+",".join(valid)+")"

    while True:
        read = input(msg + "\n")
        if valid is None or read in valid: return read
        else: print("Invalid input.")
            

def cleanWhiteSpace(content: str) -> str:
    """ Remove excessive whitespace from a document. """
    if content is None:
        return content
    content = re.sub("[ \t]+", " ", content)
    content = re.sub(" (?=[\.'!?,%])", "", content)
    return content.strip()

def cleanSentence(sentence: str) -> str:
    """ Clean a sentence by breaking up and cleaning each word individually. """
    words = sentence.split()

    cleaned = [word for rawWord in words for word in cleanWord(rawWord)]

    return " ".join(cleaned)

def cleanWord(word: str) -> str:
    """ Remove grammar and unwanted words """

    # Expand words
    word = re.sub("n't$", " not", word)

    # Remove posession
    word = re.sub("'s$", "", word)

    # Lower the case
    word = word.lower()

    # Find words and return
    cleaned = re.findall("[A-Za-z-_]+", word)

    # Ensure spelling correct
    if SpellingCorrector.WORDS:
        cleaned = [SpellingCorrector.predict(word) for word in cleaned]

    return cleaned

def split(text: str, separator: re) -> [str]:
    """ Separate the text with the separators that has been given. Replace all
    separators with a single separator and then split by the single separator
    
    Params:
        text - The string to be split
        separators - A list of separator strings to have the string split by
        
    Returns:
        str - A collection of ordered strings representing the initial text split by the
            separators
    """

    # TODO: The documentation implies this function is to take a number of Separators but it does not do that.

    split = []  # The segments of the text

    while True:
        # Match the separator
        match = separator.search(text)
        if match is None: break

        # break up the text by the separator
        s, e = match.span()
        split.append(text[:s] + match.group(0))
        text = text[e:]

    split.append(text)

    return split

class SpellingCorrector:
    """ Singleton class for the correction of words present within text """

    WORDS = None
    size = 0

    @classmethod
    def load(cls):
        if cls.WORDS is None:
            # Import the counter data type
            from .. import Document, Resources
            from collections import Counter

            def words(text):
                return re.findall("\w+", text.lower())

            cls.WORDS = Counter(words(open(Resources.DICTIONARY).read()))

            documents = [Document(filepath=path) for path in Resources.TEXT_COLLECTIONS]
            sentences = [cleanSentence(sen).split() for doc in documents for sen in doc]
            sentences = [word for sentence in sentences for word in sentence]
            cls.WORDS.update(sentences)

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