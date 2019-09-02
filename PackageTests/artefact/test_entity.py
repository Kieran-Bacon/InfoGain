import unittest
import pytest

from infogain.artefact.document2 import Entity

class Test_Entity(unittest.TestCase):

    def test_Entity(self):

        entity = Entity("A", "a")

        self.assertEqual(entity.classType, "A")
        self.assertEqual(entity.surfaceForm, "a")
        self.assertEqual(entity.confidence, 1.)

    def test_restrictedAccess(self):

        entity = Entity("A", "a")

        for prop in ["classType", "surfaceForm"]:
            with pytest.raises(AttributeError):
                setattr(entity, prop, "Something else")

        for eachType in [34, "hello", -2. -0.4, Exception]:
            with pytest.raises(ValueError):
                entity.confidence = eachType

    def test_properties(self):

        entity = Entity("A", 'a')

        entity.properties['hello'] = 'there'

        self.assertEqual(entity.properties['hello'], 'there')

        with pytest.raises(KeyError):
            entity.properties['something else']

        with pytest.raises(ValueError):
            entity.properties[10] = "something"