import unittest, pytest

from infogain.knowledge import Ontology, Concept, Instance
from infogain.knowledge.concept import ConceptSet, FamilyConceptSet, ConceptAliases, ConceptProperties
from infogain.exceptions import ConsistencyError

class Test_ConceptInterface(unittest.TestCase):

    def test_init(self):

        parent = Concept("Parent")
        child = Concept("Child")

        concept = Concept(
            "example",
            parents={parent, "String Parent"},
            children={child, "String Child"},
            aliases={"Example", "Examples"},
            properties={"key": 100},
            category="abstract"
        )

        self.assertEqual(concept.name, "example")
        self.assertEqual(concept.parents, {parent, "String Parent"})
        self.assertEqual(concept.children, {child, "String Child"})
        self.assertEqual(concept.aliases, {"Example", "Examples"})
        self.assertEqual(concept.properties, {"key": 100})
        self.assertEqual(concept.category, Concept.ABSTRACT)
    
    def test_parents(self):
        # Assert that you can collect a set of parents of the concept from the concept and not set it

        concept = Concept("example")

        self.assertIsInstance(concept.parents, FamilyConceptSet)
        
        self.assertEqual(concept.parents, set())

        parent = Concept("Parent", children={concept})

        self.assertEqual(concept.parents, {parent})

        concept.parents.remove(parent)

        self.assertEqual(concept.parents, set())

        concept.parents = {parent}

        self.assertEqual(concept.parents, {parent})

    def test_children(self):
        
        concept = Concept("example")

        self.assertIsInstance(concept.children, FamilyConceptSet)
        
        self.assertEqual(concept.children, set())

        child = Concept("Child", parents={concept})

        self.assertEqual(concept.children, {child})

        concept.children.remove(child)

        self.assertEqual(concept.children, set())

        concept.children = {child}

        self.assertEqual(concept.children, {child})

    def test_category(self):

        concept = Concept("example")

        self.assertTrue(concept.category is Concept.DYNAMIC)
        self.assertEqual(concept.category, "dynamic")

        concept.category = "static"

        self.assertTrue(concept.category is Concept.STATIC)
        self.assertEqual(concept.category, "static")

        concept.category = Concept.ABSTRACT

        self.assertTrue(concept.category is Concept.ABSTRACT)
        self.assertEqual(concept.category, "abstract")

        with pytest.raises(ValueError):
            concept.category = "Not a category"

    def test_aliases(self):

        concept = Concept("example")

        self.assertIsInstance(concept.aliases, ConceptAliases)

        concept.aliases.add("example alias")

        self.assertEqual(len(concept.aliases), 1)

        concept.aliases.remove("example alias")

        self.assertEqual(len(concept.aliases), 0)

        with pytest.raises(AttributeError):
            concept.aliases = {"something"}

    def test_properties(self):

        concept = Concept("example")

        self.assertIsInstance(concept.properties, ConceptProperties)

        self.assertEqual(len(concept.properties), 0)

        concept.properties["a"] = 1

        self.assertEqual(len(concept.properties), 1)

        del concept.properties["a"]

        self.assertEqual(len(concept.properties), 0)

        with pytest.raises(AttributeError):
            concept.properties = {}

    def test_ancestors(self):

        parent = Concept("Parent")
        concept = Concept("example", parents={parent, "another"})

        self.assertEqual(parent.ancestors(), set())
        self.assertEqual(concept.ancestors(), {parent, "another"})

    def test_descendants(self):

        child = Concept("Child")
        concept = Concept("example", children={child, "another"})

        self.assertEqual(child.descendants(), set())
        self.assertEqual(concept.descendants(), {child, "another"})

    def test_settingInstance(self):

        class PersonInstance(Instance):

            def run(self):
                return 10

        abstract = Concept("abstract", category="abstract")
        static = Concept("static", category="static")
        dynamic = Concept("dynamic")

        # Assert that non-instances cannot be st
        with pytest.raises(TypeError):
            dynamic.setInstanceClass(dict)

        # Set a correct class for each category type
        with pytest.raises(ConsistencyError):
            # No instance can be given for an abstract concept
            abstract.setInstanceClass(PersonInstance)

        # Static
        static.setInstanceClass(PersonInstance)
        staticInstanceOne = static.instance()
        staticInstanceTwo = static.instance()
        self.assertIs(staticInstanceOne, staticInstanceTwo)

        # Dynamic
        dynamic.setInstanceClass(PersonInstance)
        dynamicInstanceOne = dynamic.instance()
        dynamicInstanceTwo = dynamic.instance()
        self.assertIsNot(dynamicInstanceOne, dynamicInstanceTwo)

        self.assertEqual(staticInstanceOne.run(), 10)
        self.assertEqual(dynamicInstanceTwo.run(), 10)

    def test_instance(self):

        static = Concept("Static", category="static")
        dynamic = Concept("Dynamic")

        self.assertIsInstance(static.instance(), Instance)
        self.assertIs(static.instance("example"), static.instance("another name"))

        self.assertIsInstance(dynamic.instance(), Instance)
        self.assertIsNot(dynamic.instance(), dynamic.instance())

        instanceOne = dynamic.instance("name", properties={"a": 1})
        self.assertEqual(instanceOne.name, "name")
        self.assertEqual(instanceOne.properties["a"], 1)

        instanceTwo = dynamic.instance("name", properties={"b": 2})
        self.assertEqual(instanceTwo.name, "name")
        self.assertEqual(instanceTwo.properties["b"], 2)

        self.assertFalse("a" in instanceTwo.properties)
        self.assertFalse("a" in dynamic.properties)

    def test_clone(self):

        parent = Concept("Parent")
        concept = Concept("example", parents={parent}, properties={"a": 1}, aliases=["alias"], category="static")

        clone = concept.clone()

        self.assertEqual(concept.name, clone.name)
        self.assertEqual(clone.parents, {"Parent"})
        self.assertEqual(clone.children, set())
        self.assertEqual(concept.aliases, clone.aliases)
        self.assertEqual(concept.properties, clone.properties)
        self.assertEqual(concept.category, clone.category)
        self.assertFalse(concept is clone)

class Test_Concept(unittest.TestCase):

    def test_initialisation_family_linking(self):

        person = Concept("Person", children={"Kieran", "Luke"})
        kieran = Concept("Kieran", parents={person})

        self.assertTrue(kieran in person.children)
        self.assertTrue(person in kieran.parents)
        self.assertTrue("Luke" in person.children)

    def test_ancestors_full_concepts(self):

        grandfather = Concept("Grand Father")
        father = Concept("Father", parents={grandfather})
        child = Concept("Child", parents={father})

        self.assertEqual(child.ancestors(), {grandfather, father})

    def test_ancestors_partial_concepts(self):

        father = Concept("Father", parents={"Grand Father"})
        child = Concept("Child", parents={father})

        self.assertEqual(child.ancestors(), {father, "Grand Father"})

        child = Concept("Child", parents={"John"})

        self.assertEqual(child.ancestors(), {"John"})

    def test_descendants_full_concepts(self):

        grandson = Concept("Grand Son")
        son = Concept("Son", children={grandson})
        person = Concept("Person", children={son})

        self.assertEqual(person.descendants(), {son, grandson})

    def test_descendants_partial_concepts(self):

        son = Concept("Son", children={"Grand Son"})
        person = Concept("Person", children={son})

        self.assertEqual(person.descendants(), {son, "Grand Son"})

        person = Concept("Person",children={"Son"})
        self.assertEqual(person.descendants(), {"Son"})

    def test_expandConceptSet(self):
        """ Ensure that a concept is correct expanded into its children """

        ont = Ontology()

        x = Concept("x")
        x1, x2 = Concept("x1", {x}), Concept("x2", {x})
        x11, x12 = Concept("x11", {x1}), Concept("x12", {x1})

        y = Concept("y")
        y1, y2 = Concept("y1", {y}), Concept("y2", {y})
        y11 = Concept("y11", {y1})

        for concept in {x,x1,x11,x2,x12,y,y1,y11,y2}:
            ont.concepts.add(concept)

        self.assertEqual(
            {con.name for con in ConceptSet({x, y1}).expanded()},
            {con.name for con in {x,x1,x2,x11,x12,y1,y11}}
        )
        self.assertEqual(ConceptSet({x2, y}).expanded(), {x2, y, y1, y2, y11})

    def test_generation_of_concept_instance(self):
        """ Test that a concept generates its instance correctly and that it has the behaviour that
        we would want """

        # Test that an abstract concept raises an type error when attempting to generate its instance
        being = Concept("Being", properties={"age": int}, category="abstract")
        with pytest.raises(TypeError):
            being.instance()

        # Test that a static concept returns only a single instance regardless of the number of calls
        kieran = Concept("Kieran", properties={"age": 10}, category="static")

        firstKieranInst = kieran.instance()
        secondKieranInst = kieran.instance()

        self.assertTrue(firstKieranInst is secondKieranInst)
        self.assertTrue(kieran.properties is firstKieranInst.properties is secondKieranInst.properties)

        kieran.properties["lastname"] = "Bacon"

        self.assertEqual(firstKieranInst.lastname, "Bacon")
        self.assertEqual(secondKieranInst.lastname, "Bacon")

        # Test that a dynamic concept generates multiple differing instances with individual properties
        person = Concept("Person", properties={"age": 10})

        ben = person.instance("Ben")
        tom = person.instance("Tom")

        person.properties["lastname"] = "Bacon"

        self.assertEqual(ben.lastname, None)  # Does not have the new property

        tom.height = 6.4

        self.assertEqual(tom.height, 6.4)
        self.assertEqual(ben.height, None)

    def test_ConceptInstance_assignment(self):

        class PersonInstance(Instance):

            def something(self):
                return 10

        self.assertTrue(issubclass(PersonInstance, Instance))

        example = Concept("example", properties={"cool": 97})

        example.setInstanceClass(PersonInstance)

        inst = example.instance()

        self.assertEqual(inst.something(), 10)

    def test_concept_string_equality_in_dictionaries(self):

        example = Concept("example")

        collection = {example: 10}

        self.assertEqual(collection.get(example), 10)
        self.assertEqual(collection.get("example"), 10)

        collection2 = {"example": 10}

        self.assertEqual(collection2.get(example), 10)
        self.assertEqual(collection2.get("example"), 10)


if __name__ == "__main__":
    unittest.main()