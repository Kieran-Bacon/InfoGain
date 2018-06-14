from ...Extraction import RelationExtractor

from .RelationExtractor_CrossValidation import RETune


def tune(object_to_tune: object, *args):

    # Factory
    if object_to_tune is RelationExtractor:
        return RETune(args[0], args[1])
    else:
        raise NotImplementedError("Tuning for that object has not been set up yet")
