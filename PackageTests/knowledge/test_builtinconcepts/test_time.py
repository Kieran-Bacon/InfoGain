import unittest, datetime

from infogain import knowledge
from infogain import cognition

class Test_Time_Builtin(unittest.TestCase):

    def setUp(self):

        self.engine = cognition.InferenceEngine()
        self.engine.importBuiltin("time")

        self.factory = cognition.evaltrees.EvalTreeFactory()

    def test_calls(self):

        example = knowledge.Concept("example", properties={"date": datetime.date(2017, 2, 1)})
        self.engine.concepts.add(example)


        for logic in ["eq(#Date('01-02-2017'), #example.date)", "eq(#example.date, #Date('01-02-2017'))"]:
            node = self.factory.constructTree(logic = logic)

            self.assertEqual(
                node.eval(
                    scenario = {
                        "#Date": self.engine.concepts["Date"].instance(),
                        "#example": example.instance()
                    }
                ),
                1.
            )

    def test_calls_return_instances_that_behave(self):

        example = knowledge.Concept("example", properties={"date": datetime.date(2017, 2, 1)})
        self.engine.concepts.add(example)

        for logic, answer in {
            "#Date('02-02-2017').before(#example.date)": False,
            "#Date('01-01-2017').before(#example.date)": True}.items():

            node = self.factory.constructTree(logic)

            self.assertEqual(
                node.eval(
                    scenario = {
                        "#Date": self.engine.concepts["Date"].instance(),
                        "#example": example.instance()
                    }
                ),
                answer
            )

    def test_pulled_down_behaviour(self):

        for logic, answer in {
            "#Date.today()": datetime.date.today(),
            "#Date('02-06-1927').isoformat()": datetime.date(1927,6,2).isoformat()
            }.items():

            node = self.factory.constructTree(logic)

            self.assertEqual(
                node.eval(
                    scenario = {
                        "#Date": self.engine.concepts["Date"].instance(),
                    }
                ),
                answer
            )







