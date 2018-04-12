import os
from InfoGain import Ontology, Document, TrainingDocument

LOCATION = os.path.dirname(os.path.realpath(__file__))
DOCUMENTS = os.path.join(LOCATION, "Resources", "Documents")
ONTOLOGIES = os.path.join(LOCATION, "Resources", "Ontologies")

with open(os.path.join(DOCUMENTS, "Predictlanguages.txt")) as filehandler:
    content = filehandler.read()

    # Split the content into paragraphs
    rawParagraphs = content.split("\n\n")

    paragraphs, cleanedParagraphs = [], []
    
    # Split the paragraphs into sentences
    for rawParagraph in rawParagraphs:
        rawSentences = paragraph.split(".")

        sentences, cleanedSentences = [], []

        # Create a cleaned version of the sentences
        for rawSentence in rawSentences:
            sentence = rawSentence.split()

            sentences.append(sentence)
            cleanedSentence = []

            # Replace some of the pronouns with the correct concepts
            # TODO: identify the words that that are meant to be replaced
            for rawWord in sentence:
                cleanedSentence.append(cleanWord(rawWord))

            cleanedSentences.append(cleanedSentence)

        paragraphs.append(sentences)
        cleanedParagraphs.append(cleanedSentences)