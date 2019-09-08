import unittest
import pytest

from infogain.artefact import Document, Entity, Annotation

class Test_DocumentPreProcessing(unittest.TestCase):

    def test_removalOfUnwantedCharacters(self):

        x, y = "this is a @£$%^*() string that shall produce =>", "this is a @£$% string that shall produce"

        self.assertEqual(Document(x).content, y)

    def test_conversionOfEndLineCharacters(self):

        x = "Imagining... A sentence with unexpected twists!? and turns. simple. yet affective!"
        y = "Imagining. A sentence with unexpected twists. and turns. simple. yet affective."

        self.assertEqual(Document(x).content, y)

    def test_directLinkingRemovalWhenApplicable(self):

        x = "Dolphins are not fish: they are warm blooded animals"
        y = "Dolphins are not fish; they are warm blooded animals"

        self.assertEqual(Document(x).content, y)

        x = "Countries I shall visit: London, England; Paris, France; LA, America."

        self.assertEqual(Document(x).content, x)

    def test_replaceSymbolShorthand(self):

        x, y = "I shall get some doritos & dip", "I shall get some doritos and dip"
        self.assertEqual(Document(x).content, y)

    def test_whitespaceReduction(self):

        x = "Something with a  lot of    spaces in every    now             and             again."
        y = "Something with a lot of spaces in every now and again."

        self.assertEqual(Document(x).content, y)

    def test_apostrophesMapper(self):

        x = "This is something that I don't like having to do, but they're making me do it."
        y = "This is something that I do not like having to do, but they are making me do it."

        self.assertEqual(Document(x).content, y)

    def test_stripingWhiteSpace(self):

        x, y = "    something amazing. \t\n", "something amazing."
        self.assertEqual(Document(x).content, y)

    def test_newlineStructionPreserved(self):

        x = "Given a passage that a that talks for a bit.\n\nAnd then another section which is apart."
        self.assertEqual(Document(x).content, x)



class Test_Document(unittest.TestCase):

    def test_DocumentLength(self):

        document = Document("I am a document that has some content. This string length should not change.")

        self.assertEqual(len(document), len(document.content))

        document.split(r"\.")

        self.assertEqual(len(document), len(document.content))

        document.join(" SEPARATOR ")

        self.assertEqual(len(document), len(document.content))

    def test_documentSentences(self):

        document = Document("""
        A passage about a king. The king was going about his day. The king didn't have any responsibilities
        """)

        sentences = [
            "A passage about a king",
            "The king was going about his day",
            "The king didn't have any responsibilities"
        ]

        for sentence, target in zip(document.sentences(), sentences):
            self.assertEqual(sentence, target)

    def test_documentWords(self):
        document = Document(content="A small document so smaller test.")

        words = ["A", "small", "document", "so", "smaller", "test"]

        for word, target in zip(document.words(), words):
            self.assertEqual(word, target)

    def test_documentSplit(self):

        content = (
            "The document content is long and erratic. There are a few sentences in the first section. And then "
            "some sentences in the second section.\n\nSection two was separated from section one by two new line "
            "characters."
        )
        sections = [
            (
                "The document content is long and erratic. There are a few sentences in the first section. And then"
                " some sentences in the second section."
            ),
            (
                "Section two was separated from section one by two new line "
                "characters."
            )
        ]
        sentences = [
            "The document content is long and erratic",
            "There are a few sentences in the first section",
            "And then some sentences in the second section",
            "Section two was separated from section one by two new line characters"
        ]
        words = [w for sentence in sentences for w in sentence.split()]

        document = Document(content)
        document.split("\n\n")

        self.assertEqual(list(iter(document)), sections)
        self.assertEqual(list(document.sentences()), sentences)
        self.assertEqual(list(document.words()), words)

    def test_splitDoubleDown(self):

        content = (
            "section 1:\nmorning:\nThis is the morning passage.\nevening:\nAnother passage.\n\n"
            "section 2:\nmorning:\nSecond morning passage.\nevening:\nSecond evening passage."
        )

        sections = [
            "This is the morning passage.",
            "Another passage.",
            "Second morning passage.",
            "Second evening passage."
        ]
        sentences = [s[:-1] for s in sections]
        words = [w for s in sentences for w in s.split()]

        document = Document(content=content)
        document.split(r"section \d:")
        document.split("(morning|evening):")

        self.assertEqual(list(iter(document)), sections)
        self.assertEqual(list(document.sentences()), sentences)
        self.assertEqual(list(document.words()), words)

    def test_documentSplitForwordBackward(self):

        content = (
            "A line to be split by a SEPARATOR test to see the side the separator goes to"
        )

        sections = [
            "A line to be split by a",
            "test to see the side the separator goes to",
        ]

        def forwardCheck(document):
            if document.breaktext == "":
                self.assertEqual(document.content, sections[0])
            else:
                self.assertEqual(document.content, sections[1])

        document = Document(content=content)
        document.split(r"SEPARATOR", key=forwardCheck)

        def backwardCheck(document):
            if document.breaktext == "":
                self.assertEqual(document.content, sections[1])
            else:
                self.assertEqual(document.content, sections[0])

        document = Document(content=content)
        document.split(r"SEPARATOR", key=backwardCheck, forward=False)

    def test_documentJoin(self):

        content = (
            "A line to be split by a SEPARATOR test to see the side the separator goes to"
        )

        # Basic separator
        document = Document(content=content)
        document.split(r"SEPARATOR")

        document.join(" JOINING STRING ")

        self.assertEqual(
            document.content,
            "A line to be split by a JOINING STRING test to see the side the separator goes to"
        )

        # Complex separator
        document = Document(content=content)
        document.split(r"SEPARATOR")

        def joining(document1, document2):
            content = document1.content + " " + document2.breaktext + str(len(document2.content)) + " " + document2.content
            return Document(content)

        document.join(joining)

        self.assertEqual(
            document.content,
            "A line to be split by a SEPARATOR42 test to see the side the separator goes to"
        )

    def test_documentJoinDoubleDown(self):

        content = (
            "section 1:\nmorning:\nThis is the morning passage.\nevening:\nAnother passage.\n\n"
            "section 2:\nmorning:\nSecond morning passage.\nevening:\nSecond evening passage."
        )

        document = Document(content=content)
        document.split(r"section \d:")
        document.split("(morning|evening):")

        # Join bottom level
        document.join("\n")

        sections = [
            "This is the morning passage.\nAnother passage.",
            "Second morning passage.\nSecond evening passage."
        ]

        for docSec, sec in zip(iter(document), sections):
            self.assertEqual(docSec, sec)

        # Join top level with function
        def joining(doc1, doc2):
            content = doc1.breaktext + "\n" if doc1.breaktext else ""
            content += doc1.content + "\n\n" + doc2.breaktext + "\n" + doc2.content
            return Document(content)

        document.join(joining)

        remade = (
            "section 1:\nThis is the morning passage.\nAnother passage.\n\n"
            "section 2:\nSecond morning passage.\nSecond evening passage."
        )

        self.assertEqual(document.content, remade)

