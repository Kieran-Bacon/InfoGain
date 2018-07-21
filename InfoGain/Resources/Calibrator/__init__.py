from ...Extraction import RelationExtractor

from .RelationExtractor_CrossValidation import RETune


def tune(object_to_tune: object, *args) -> "Scores":
    """ Factory function that runs the apprioprate function for the object provided. Turn the object
    such that for the training information provided, it provides the best scores.
    
    Params:
        object_to_turn (object) - The class of the object to be tuned
        args ([arguments]) - The arguments to be passed to the tuning function
        
    Returns:
        Scores - The chosen parameters and the scores of the various arrangements
    """

    # Factory
    if object_to_tune is RelationExtractor:
        return RETune(args[0], args[1])
    else:
        raise NotImplementedError("Tuning for that object has not been set up yet")
