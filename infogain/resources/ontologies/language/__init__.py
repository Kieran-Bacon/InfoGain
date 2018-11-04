import os
from ....knowledge import Ontology
from ....artefact import Document

ROOT = os.path.dirname(os.path.realpath(__file__))

def ontology(get_path: bool = False) -> Ontology:
    """ Load and return the language ontology, keep the ontology loaded for quick return if
    promted again 
    
    Params:
        get_path (str) - A toggle to inform where the path to the ontology should be returned
    
    Returns:
        Ontology - the ontology object of the domain
        str - The path, may be returned
        """
    path = os.path.join(ROOT, "ontology.json")

    if get_path: return Ontology(filepath=path), path
    else: return Ontology(filepath=path)

def training(num_of_docs: int = None) -> [Document]:
    """ Load and store training documents for the domain

    Params:
        num_of_documents (int) - The number of training documents to be returned
    
    Returns:
        [Document] - A collection of training documents for this domain
    """

    trainingFiles = os.listdir(os.path.join(ROOT, "training"))
    trainingFiles.remove("__init__.py")
    trainingFiles.remove("__pycache__")

    if num_of_docs: trainingFiles = trainingFiles[:num_of_docs]

    return [Document(filepath=os.path.join(ROOT, "training", filename))
        for filename in trainingFiles]

def testing(num_of_docs: int = None) -> [Document]:
    """ Load and store un-annotated documents from the domain to act as documents to predict
    on

    Params:
        num_of_docs (int) - The number of documents to return from the collection
    
    Returns:
        [Document] - The collection of documents to predict upon
    """

    testingFiles = os.listdir(os.path.join(ROOT, "testing"))
    testingFiles.remove("__init__.py")
    testingFiles.remove("__pycache__")

    if num_of_docs: testingFiles = testingFiles[:num_of_docs]

    return [Document(filepath=os.path.join(ROOT, "testing", filename))
        for filename in testingFiles]