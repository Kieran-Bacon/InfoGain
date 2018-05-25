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

        self._domains, self._targets = [], []

        if isinstance(domains, set) and isinstance(targets, set):
            domains, targets = [domains], [targets]

        for group in domains:
            groupSet = group.copy()
            [groupSet.add(con) for dom in group for con in dom.descendants() if not con.permeable]
            self._domains.append(groupSet)

        for group in targets:
            groupSet = group.copy()
            [groupSet.add(con) for tar in group for con in tar.descendants() if not con.permeable]
            self._targets.append(groupSet)

    def domains(self, dom: Concept = None) -> None:
        """ Return the domain concepts linked with the relation """
        return set([con for group in self._domains for con in group])

    def targets(self, tar: Concept = None) -> None:
        """ Return the target concepts linked with the relation """

        return set([con for group in self._targets for con in group])

    def hasDomainTargetPair(self, domain: Concept, target: Concept) -> bool:
        """ Check that the relationship holds between two concepts """

        for domains, targets in zip(self._domains, self._targets):
            if domain in domains and target in targets:
                return True

        return False

    def hasDomain( self, concept: Concept) -> bool:
        """ Checked concept membership to the relation as a domain """
        return concept in self.domains()

    def hasTarget( self, concept: Concept) -> bool:
        """ Checks concept membership to the relation as a target """
        return concept in self.targets()

    def subscribe( self, concept: Concept) -> None:
        """ Intellegently links concept with domain or target based on 
        relative linkage """

        if concept.permeable: return # Ensure concept is meant to be viewable

        # Link concept with any pairing group applicable
        for domains, targets in zip(self._domains, self._targets):
            if domains.intersection(concept.parents): domains.add(concept)
            if targets.intersection(concept.parents): targets.add(concept)

    def instance(self, domain: Concept, target: Concept):
        """ Return a relation instance if applicable """
        if self.hasDomainTargetPair(domain, target):
            return RelationInstance(domain, self, target)

    def minimise(self) -> dict:
        """ Return only the information the relation represents """

        domains = [[con.name for con in group] for group in self._domains]
        targets = [[con.name for con in group] for group in self._targets]

        if len(self._domains) == 1:
            domains, targets = domains[0], targets[0]

        relation = {
            "domain": domains,
            "target": targets
        }

        if len(self._domains) > 1:
            relation["sets"] = True
            
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