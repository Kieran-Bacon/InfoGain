import unittest

from infogain.knowledge import Concept, Instance, Relation

from infogain.cognition import InferenceEngine
from infogain.cognition.evaltrees import EvalTreeFactory
from infogain.cognition.treenodes.conceptnode import ConceptNode

class Test_OperatorNode(unittest.TestCase):

    def setUp(self):
        self.factory = EvalTreeFactory()

    def test_equal_operator(self):

        node = self.factory.constructTree("20 == 19")

        self.assertEqual(node.eval(scenario={}), False)

        node = self.factory.constructTree("20 == 20")

        self.assertEqual(node.eval(scenario={}), True)

    def test_not_equal_operator(self):

        node = self.factory.constructTree("20 != 19")

        self.assertEqual(node.eval(scenario={}), True)

        node = self.factory.constructTree("20 != 20")

        self.assertEqual(node.eval(scenario={}), False)

