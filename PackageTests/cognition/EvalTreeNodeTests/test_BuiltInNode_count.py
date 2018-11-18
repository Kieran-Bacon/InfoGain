import unittest

from infogain.cognition import InferenceEngine
from infogain.cognition.evalrule import EvalRule
from infogain.cognition.evaltrees import EvalTreeFactory

from infogain.resources.ontologies import school as resouce

class test_BuiltinNode_count(unittest.TestCase):
    
    def setUp(self):
        self.school = InferenceEngine(ontology=resouce.ontology())

        concept_person = self.school.concept("Person")
        concept_class = self.school.concept("Class")
        inst_english = concept_class.instance("English")
        self.school.addInstance(inst_english)

        people = [
            concept_person.instance("Kieran", {"age": 15}),
            concept_person.instance("Luke", {"age": 22}),
            concept_person.instance("Steven", {"age": 14}),
            concept_person.instance("Zino", {"age": 27})
        ]
        for p in people: self.school.addInstance(p)

        relation_enrolledOn = self.school.relation("enrolled_on")

        relation_enrolledOn.addRule(EvalRule({self.school.instance("Kieran")}, {inst_english}, 100))
        relation_enrolledOn.addRule(EvalRule({self.school.instance("Luke")}, {inst_english}, 100))

        self.factory = EvalTreeFactory(self.school)

    def test_count_instances(self):

        node = self.factory.constructTree("count(#Person)")
        self.assertEqual(node.eval(), 4)

    def test_count_instances_with_filters(self):

        node = self.factory.constructTree("count(#Person, #Person.age >= 15, #Person.age <= 25)")
        self.assertEqual(node.eval(), 2)

    def test_count_relations(self):

        node = self.factory.constructTree("count(#Person=teaches=#Class)")
        self.assertEqual(node.eval(), 0)

        node = self.factory.constructTree("count(#Person=enrolled_on=#Class)")
        self.assertEqual(node.eval(), 2)

    def test_count_relations_with_domain_target(self):
        pass

    def test_count_relations_with_filters(self):
        pass