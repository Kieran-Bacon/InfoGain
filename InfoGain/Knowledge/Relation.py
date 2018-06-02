from . import MissingConcept
from .Concept import Concept

class Relation:
    """ A relation expresses a connection between concepts.
    
    Args:
        domains (set): A collection of concepts
        name (str): The name to identify the relation object
        targets (set): A collection of concepts
    """

    def __init__(self, domains: {Concept}, name: str, targets: {Concept}):

        self.name = name
        self.domains = domains.copy()
        self.targets = targets.copy()

        def addConcept(collection: set, con: Concept):

                if isinstance(con, Concept):
                    # Add if the concept is readable
                    if not con.permeable: collection.add(con)

                    # For all the descendants of the concept
                    for child in con.descendants():
                        if isinstance(child, Concept) and child.permeable:
                            continue
                        # add if they are not permeable  
                        collection.add(child)
                else:
                    collection.add(con)

        [addConcept(self.domains, con) for con in domains]
        [addConcept(self.targets, con) for con in targets]

        if not self.domains or not self.targets:
            raise MissingConcept("The relationship doesn't have a domain to target pairing, consider the permeable-ness of the concepts")

    def between(self, domain: Concept, target: Concept) -> bool:
        """ Verify if the relationship holds between two concepts """
        if domain.permeable or target.permeable: return False
        return domain in self.domains and target in self.targets

    def subscribe( self, concept: Concept) -> None:
        """ Intellegently links concept with domain or target based on 
        relative linkage """

        if concept.permeable: return # Ensure concept is meant to be viewable

        # Add the concept into the concept stores if one of its ancestors is present
        ancestors = concept.ancestors()
        if self.domains.intersection(ancestors): self.domains.add(concept)
        if self.targets.intersection(ancestors): self.targets.add(concept)

    def minimise(self) -> dict:
        """ Return only the information the relation represents """

        domains, targets = set(), set()

        def minimise_collection(collection, expanded):
            for concept in expanded:
                # Check if the concept's ancestors overlap with the collection
                # If so, they are already expressed by the collection, do nothing
                if not concept.ancestors().intersection(collection):
                    
                    # Add concept to collection to express it
                    collection.add(concept)

                    # For every child element that is expressed, remove concept now covers it
                    [collection.remove(child) for child in concept.descendants().intersection(collection)]

        minimise_collection(domains, self.domains)
        minimise_collection(targets, self.targets)

        domains = [con.name for con in domains]
        targets = [con.name for con in targets]

        return {"domains": domains, "name": self.name, "targets": targets}