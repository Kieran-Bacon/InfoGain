import unittest
import pytest

from infogain.artefact import Entity, Annotation, Document

class Test_DocumentEntities(unittest.TestCase):

    def setUp(self):
        self.document = Document("This is a document with two sentences. With lots of content.")

        self.documentEntity = Entity("Artefact", "document")
        self.sentencesEntity = Entity("Artefact", "sentences")
        self.contentEntity = Entity("Artefact", "content")

    def test_addEntities(self):

        # Add entity to the document with the index of the word
        self.document.entities.add(self.documentEntity, 10)

        self.assertEqual(len(self.document.entities), 1)
        self.assertIs(next(iter(self.document.entities)), self.documentEntity)

        with pytest.raises(ValueError):
            self.document.entities.add(Entity("Fake", "not Present"))

    def test_setContains(self):

        # Add entity top level and check that it is a member of the document entities
        self.document.entities.add(self.documentEntity, 10)
        self.assertIn(self.documentEntity, self.document.entities)

        # Split the document and ensure that the entity is still a member of the document entities
        self.document.split(r'\.')
        self.assertIn(self.documentEntity, self.document.entities)

        # Add an entity at the split level and assert the the entity is a member of the document entities
        self.document.entities.add(self.contentEntity, 52)
        self.assertIn(self.contentEntity, self.document.entities)

    def test_addSentenceEntities(self):

        for sentence in self.document.sentences():
            if sentence.find("sentences") > -1:
                self.document.entities.add(self.sentencesEntity, sentence.find("sentences"))

            else:
                self.document.entities.add(self.contentEntity, sentence.find("content"))

        self.assertEqual(len(self.document.entities), 2)
        self.assertEqual(list(self.document.entities), [self.sentencesEntity, self.contentEntity])

    def test_addWordEntities(self):

        for word in self.document.words():
            if word == "document":
                self.document.entities.add(self.documentEntity)
            elif word == 'sentences':
                self.document.entities.add(self.sentencesEntity)
            elif word == 'content':
                self.document.entities.add(self.contentEntity)

        self.assertEqual(len(self.document.entities), 3)
        self.assertEqual(list(self.document.entities), [self.documentEntity, self.sentencesEntity, self.contentEntity])

    def test_addEntityToSub(self):

        self.document.split(r"\.")

        self.document.entities.add(self.documentEntity, 10)
        self.document.entities.add(self.contentEntity, 52)

        with pytest.raises(ValueError):
            self.document.entities.add(Entity("Fake", "Fake"), 30)

        self.assertEqual(len(self.document.entities), 2)
        self.assertEqual(list(self.document.entities), [self.documentEntity, self.contentEntity])

    def test_entitiesOnSplit(self):

        self.document.entities.add(self.documentEntity, 10)
        self.document.entities.add(self.contentEntity, 52)

        data = iter([
            ("This is a document with two sentences", self.documentEntity),
            ("With lots of content", self.contentEntity)
        ])

        def entityTester(document):
            try:
                content, entity = next(data)
            except:
                return # Last document has 0 content - just return for it
            self.assertEqual(document.content, content)
            self.assertEqual(len(document.entities), 1)
            self.assertIs(next(iter(document.entities)), entity)

        self.document.split(r"\.", key = entityTester)

        self.assertEqual(len(self.document.entities), 2)
        self.assertEqual(list(self.document.entities), [self.documentEntity, self.contentEntity])

    def test_entitiesOnJoin(self):

        self.document.split(r"\.")

        self.document.entities.add(self.documentEntity, 10)
        self.document.entities.add(self.contentEntity, 52)

        self.document.join(" SEPARATOR ")

        self.assertEqual(len(self.document.entities), 2)
        self.assertEqual(list(self.document.entities), [self.documentEntity, self.contentEntity])

    def test_removeEntity(self):

        self.document.entities.add(self.documentEntity, 10)

        self.assertEqual(len(self.document.entities), 1)
        self.assertEqual(list(self.document.entities), [self.documentEntity])

        self.document.entities.remove(self.documentEntity)

        self.assertEqual(len(self.document.entities), 0)
        self.assertEqual(list(self.document.entities), [])


    def test_removeEntitySplit(self):

        self.document.split(r"\.")
        self.document.entities.add(self.documentEntity, 10)
        self.document.entities.add(self.contentEntity, 52)

        self.assertEqual(len(self.document.entities), 2)
        self.assertEqual(list(self.document.entities), [self.documentEntity, self.contentEntity])

        self.document.entities.remove(self.documentEntity)

        self.assertEqual(len(self.document.entities), 1)
        self.assertEqual(list(self.document.entities), [self.contentEntity])

    def test_removeEntityAnnotation(self):

        self.document.entities.add(self.documentEntity, 10)
        self.document.entities.add(self.sentencesEntity, 28)
        self.document.entities.add(self.contentEntity, 52)

        ann = Annotation(self.documentEntity, "x", self.sentencesEntity)

        self.document.annotations.add(ann)

        self.assertEqual(len(self.document.entities), 3)
        self.assertEqual(list(self.document.entities), [self.documentEntity, self.sentencesEntity, self.contentEntity])
        self.assertEqual(len(self.document.annotations), 1)
        self.assertEqual(list(self.document.annotations), [ann])

        self.document.entities.remove(self.sentencesEntity)

        self.assertEqual(len(self.document.entities), 2)
        self.assertEqual(list(self.document.entities), [self.documentEntity, self.contentEntity])
        self.assertEqual(len(self.document.annotations), 0)
        self.assertEqual(list(self.document.annotations), [])

    def test_entityIndexes(self):

        entities = [(self.documentEntity, 10), (self.sentencesEntity, 28), (self.contentEntity, 52)]

        for e, i in entities:
            self.document.entities.add(e, i)

        for (i, e), (e2, i2) in zip(self.document.entities.indexes(), entities):
            self.assertEqual((i, e), (i2, e2))

        self.document.split(r"\.")

        for (i, e), (e2, i2) in zip(self.document.entities.indexes(), entities):
            self.assertEqual((i, e), (i2, e2))

    def test_entityAddingOutOfOrder(self):

        entities = [(self.sentencesEntity, 28), (self.contentEntity, 52), (self.documentEntity, 10)]

        for e1, e2 in zip(self.document.entities, [self.documentEntity, self.sentencesEntity, self.contentEntity]):
            self.assertIs(e1, e2)