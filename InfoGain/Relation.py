from .Concept import Concept

class Relation:
    """ A relation object expresses and contains all the concepts that
    the relation may form between. """

    def __init__(self, domains: {Concept}, name: str, targets: {Concept}):
        """ Initialise the realtion object and handle the linking of descendant concepts
        to the relation

        Params:
            - domains: list of top level domain objects
            - name: the name to identify the relation object
            - targets: list of top level target objects
        """

        self.name = name

        # Unpackage all descendant concepts linked with relation.
        self._domains = domains.copy()
        [self._domains.add(con) for dom in domains for con in dom.descendants() if not con.permeable]
        self._targets = targets.copy()
        [self._targets.add(con) for tar in targets for con in tar.descendants() if not con.permeable]

    def domains(self, dom: Concept = None) -> None:
        """ Return the domain concepts linked with the relation """
        if not dom is None:
            self._domains.add(dom)
            [self._domains.add(con) for con in dom.descendants() if not con.permeable]
            return

        return self._domains

    def targets(self, tar: Concept = None) -> None:
        """ Return the target concepts linked with the relation """
        if not tar is None:
            self._targets.add(tar)
            [self._targets.add(con) for con in tar.descendants() if not con.permeable]
            return

        return self._targets

    def hasDomain( self, concept: Concept) -> bool:
        """ Checked concept membership to the relation as a domain """
        return concept in self._domains

    def hasTarget( self, concept: Concept) -> bool:
        """ Checks concept membership to the relation as a target """
        return concept in self._targets

    def subscribe( self, concept: Concept) -> None:
        """ Intellegently links concept with domain or target based on 
        relative linkage """

        if concept.permeable: return # Ensure concept is meant to be viewable

        # Link with domain and/or if applicable target
        if self._domains.intersection(concept.parents): self._domains.add(concept)
        if self._targets.intersection(concept.parents): self._targets.add(concept) 

    def instance(self, domain: Concept, target: Concept):
        """ Return a relation instance if applicable """
        if self.hasDomain(domain) and self.hasTarget(target):
            return RelationInstance(domain, self, target)

    def minimise(self) -> dict:
        """ Return only the information the relation represents """
        relation = {
            "domain": [con.name for con in self._domains],
            "target": [con.name for con in self._targets]
        }
        return relation

class RelationInstance:
    """ A relation instances describes one of a relations possible definitions """

    def __init__(self, domain: Concept, relation: Relation, target: Concept):
        """ Initialise the instance varibles """
        
        self.domain = domain
        self.relation = relation
        self.target = target

    def __str__(self):
        """ signiture of the relation instance """
        return " ".join([self.domain.name, self.relation.name, self.target.name])

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self))