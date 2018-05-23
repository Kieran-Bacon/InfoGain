import os
ROOT = os.path.dirname(os.path.realpath(__file__))


def ontology():
    from InfoGain import Ontology

    return Ontology(filepath=os.path.join(ROOT, "./languages.json"))

def getTraining(num_of_docs=None):
    import os
    from InfoGain import TrainingDocument

    files = os.listdir(os.path.join(ROOT, "training"))
    if num_of_docs: files = files[:num_of_docs]

    for name in files:
        yield TrainingDocument(filename=os.path.join(ROOT, "training", name))

def getTesting(num_of_docs=None):
    import os
    from InfoGain import Document

    files = os.listdir(os.path.join(ROOT, "testing"))
    if num_of_docs: files = files[:num_of_docs]

    for name in files:
        yield Document(filepath=os.path.join(ROOT, "testing", name))