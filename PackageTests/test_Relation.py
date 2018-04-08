import unittest

from InfoGain import Concept, Relation

class Test_Relation(unittest.TestCase):

    def setUp(self):

        self.person = Concept("Person")
        self.dave = Concept("Dave")
        self.karen = Concept("Karen")
        self.domain_viewless = Concept("Not viewable domain", {"permeable": True})
        
        self.person.addChild(self.dave)
        self.person.addChild(self.karen)
        self.person.addChild(self.domain_viewless)
        self.dave.addParent(self.person)
        self.karen.addParent(self.person)
        self.domain_viewless.addParent(self.person)

        self.vehicle = Concept("Vehicle")
        self.car = Concept("Car")
        self.truck = Concept("Truck")
        self.target_viewless = Concept("Not viewable target", {"permeable":True})

        self.vehicle.addChild(self.car)
        self.vehicle.addChild(self.truck)
        self.vehicle.addChild(self.target_viewless)
        self.car.addParent(self.vehicle)
        self.truck.addParent(self.vehicle)
        self.target_viewless.addParent(self.vehicle)

        self.drives = Relation({self.person},"drives",{self.vehicle})

    def test_domains(self):
        self.assertEqual(Relation({},"test",{}).domains(), {})
        self.assertEqual(self.drives.domains(),{self.person, self.dave, self.karen})

    def test_targets(self):
        self.assertEqual(Relation({},"test",{}).targets(), {})
        self.assertEqual(self.drives.targets(),{self.vehicle,self.car,self.truck})

    def test_hadDomain(self):
        self.assertTrue(self.drives.hasDomain(self.person))
        self.assertFalse(self.drives.hasDomain(self.vehicle))

    def test_hasTarget(self):
        self.assertTrue(self.drives.hasTarget(self.vehicle))
        self.assertFalse(self.drives.hasTarget(self.person))

    def test_subscribe(self):
        domtar_concept = Concept("double trouble")
        dom_concept = Concept("Dom")
        tar_concept = Concept("Tar")

        domtar_concept.addParent(self.person)
        domtar_concept.addParent(self.vehicle)
        dom_concept.addParent(self.person)
        tar_concept.addParent(self.vehicle)

        self.drives.subscribe(domtar_concept)
        self.drives.subscribe(dom_concept)
        self.drives.subscribe(tar_concept)

        self.assertTrue(self.drives.hasDomain(domtar_concept))
        self.assertTrue(self.drives.hasTarget(domtar_concept))
        self.assertTrue(self.drives.hasDomain(dom_concept))
        self.assertTrue(self.drives.hasTarget(tar_concept))

    def test_permeable_subscribe(self):

        permeable_testConcept = Concept("permeable", {"permeable":True})
        dom_testConcept = Concept("dom")
        tar_testConcept = Concept("tar")

        permeable_testConcept.addParent(self.person)
        dom_testConcept.addParent(self.domain_viewless)
        tar_testConcept.addParent(self.target_viewless)

        self.drives.subscribe(permeable_testConcept)
        self.drives.subscribe(dom_testConcept)
        self.drives.subscribe(tar_testConcept)

        self.assertFalse(self.drives.hasDomain(permeable_testConcept))
        self.assertFalse(self.drives.hasDomain(dom_testConcept))
        self.assertFalse(self.drives.hasTarget(tar_testConcept))

    def test_instance(self):
        instanceString = str(self.drives.instance(self.person,self.vehicle))
        self.assertEqual(instanceString,"Person drives Vehicle")

if __name__ == "__main__":
    unittest.main()