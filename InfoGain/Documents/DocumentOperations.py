import re

# Document specific definitions
PARAGRAPH = re.compile("[\n\n]")
SENTENCE = re.compile("(?!\w+)[.?!][^\w+]")

def cleanWhiteSpace(content: str) -> str:
    """ Remove excessive whitespace from a document. """
    content = re.sub("[ \t]+", " ", content)
    content = re.sub(" (?=[\.'!?,%])", "", content)
    return content.strip()

def cleanSentence(sentence: str) -> str:
    """ Clean a sentence by breaking up and cleaning each word individually. """
    words = sentence.split()
    cleanedWords = []
    for word in words:
        cleaned = cleanWord(word)
        if cleaned:
            cleanedWords.append(cleaned)

    return " ".join(cleanedWords)

def cleanWord(word: str) -> str:
    """ Remove grammar and unwanted words """
    clean = re.search("\w+-\w+|\w+", word)
    if clean is None: return None
    return clean.group(0).lower()

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
        split.append(text[:s])
        text = text[e:]

    split.append(text)

    return split