import unittest

from infogain.cognition import InferenceEngine
from infogain.cognition.evalrule import EvalRule
from infogain.cognition.evaltrees import EvalTreeFactory

from infogain.resources.ontologies import school as resouce

class test_BuiltinNode_count(unittest.TestCase):

    def setUp(self):
        self.school = InferenceEngine(ontology=resouce.ontology())

        concept_person = self.school.concepts["Person"]
        concept_class = self.school.concepts["Class"]
        inst_english = concept_class.instance("English", {"grade": 4})
        self.school.instances.add(inst_english)

        people = [
            concept_person.instance("Kieran", {"age": 15}),
            concept_person.instance("Luke", {"age": 22}),
            concept_person.instance("Steven", {"age": 14}),
            concept_person.instance("Zino", {"age": 27})
        ]
        for p in people: self.school.instances.add(p)

        relation_enrolledOn = self.school.relations("enrolled_on")

        relation_enrolledOn.rules.add(EvalRule({self.school.instances["Kieran"]}, {inst_english}, 1.))
        relation_enrolledOn.rules.add(EvalRule({self.school.instances["Luke"]}, {inst_english}, 1.))

        self.factory = EvalTreeFactory()

    def test_count_instances(self):

        node = self.factory.constructTree("count(#Person)")
        self.assertEqual(node.eval(engine = self.school), 4)

    def test_count_instances_with_filters(self):

        node = self.factory.constructTree("count(#Person, #Person.age >= 15, #Person.age <= 25)")
        self.assertEqual(node.eval(engine = self.school), 2)

    def test_count_relations(self):

        node = self.factory.constructTree("count(#Person=teaches=#Class)")
        self.assertEqual(node.eval(engine = self.school), 0)

        node = self.factory.constructTree("count(#Person=enrolled_on=#Class)")
        self.assertEqual(node.eval(engine = self.school), 2)

    def test_count_relations_with_domain_target(self):

        node = self.factory.constructTree("count(%=enrolled_on=#Class)")
        self.assertEqual(node.eval(engine = self.school, scenario={"%": self.school.instances["Kieran"]}), 1)

        node = self.factory.constructTree("count(%=enrolled_on=#Class)")
        self.assertEqual(node.eval(engine = self.school, scenario={"%": self.school.instances["Zino"]}), 0)

    def test_count_relations_with_filters(self):

        node = self.factory.constructTree("count(#Person=enrolled_on=#Class, #Person.age < 20)")
        self.assertEqual(node.eval(engine = self.school), 1)

        node = self.factory.constructTree("count(%=enrolled_on=#Class, #Class.grade < 2)")
        self.assertEqual(node.eval(engine = self.school, scenario={"%": self.school.instances["Kieran"]}), 0)

        node = self.factory.constructTree("count(%=enrolled_on=#Class, #Class.grade > 2)")
        self.assertEqual(node.eval(engine = self.school, scenario={"%": self.school.instances["Kieran"]}), 1)