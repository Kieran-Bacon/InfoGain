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
        self.domains = set()
        self.targets = set()

        # Expand domains where applicable
        for con in domains:

            # For the domain concept
            if isinstance(con, str):
                self.domains.add(con)
                continue
            elif not con.permeable:
                self.domains.add(con)

            # For the domain concept descendants
            for dom in con.descendants():
                if isinstance(dom, str): 
                    self.domains.add(dom)
                    continue
                if not dom.permeable: self.domains.add(dom)

        # Expand targets where applicable
        for con in targets:
            # For the domain concept
            if isinstance(con, str):
                self.targets.add(con)
                continue
            elif not con.permeable:
                self.targets.add(con)

            # For the domain concept descendants
            for tar in con.descendants():
                if isinstance(tar, str):
                    self.targets.add(tar)
                    continue
                if not tar.permeable: self.targets.add(tar)

        if not self.domains or not self.targets:
            raise MissingConcept("The relationship doesn't have a domain to target pairing, consider the permeable-ness of the concepts")

    def between(self, domain: Concept, target: Concept) -> bool:
        """ Verify if the relationship holds between two concepts """
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

        for dom in self.domains:
            if not domains.intersection(dom.ancestors()):
                domains.add(dom)
                [domains.remove(con) for con in domains.intersection(dom.descendants())]

        for tar in self.targets:
            if not targets.intersection(tar.ancestors()):
                targets.add(tar)
                [targets.remove(con) for con in targets.intersection(tar.descendants())]

        domains = [con.name for con in domains]
        targets = [con.name for con in targets]

        return {"domains": domains, "name": self.name, "targets": targets}