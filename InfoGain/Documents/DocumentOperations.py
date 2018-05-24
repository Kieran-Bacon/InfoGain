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
    return re.findall("[A-Za-z-_]+", word)

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