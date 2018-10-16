import argparse

# TODO: Correct imports - build hierachy of ArgParsers

parser = argparse.ArgumentParser(
    prog="InfoGain",
    description="Information Gain - Extract information from text sources"
)

parser.add_argument(
    "-a", "--annotate",
    nargs=2,
    metavar=("OntologyPath", "DocumentPath"),
    help="Annotate a document acording to an ontology."
)

parser.add_argument(
    "-s", "--score",
    nargs=2,
    metavar=("OntologyPath", "DocumentPath"),
    help="Produce metric results for a document, according to an ontology"
)

parser.add_argument(
    "-v", "--verbose",
    help="Make the methods print out all available information."
)

args = vars(parser.parse_args())

if args["annotate"]:

    from .Documents import annotate, Document
    from .Knowledge import Ontology

    annotate(Ontology(filepath=args["annotate"][0]), Document(filepath=args["annotate"][1]))

if args["score"]:

    from .Documents import score, Document
    from .Knowledge import Ontology

    score(Ontology(filepath=args["score"][0]), Document(filepath=args["score"][0]), pprint=True)