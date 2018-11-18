import argparse
import sys

parser = argparse.ArgumentParser(
    prog="InfoGain",
    description="Information Gain - Extract information\n"
)

parser.add_argument(
    "command",
    help="Select a command to run:\n\tDocument"
)

args = parser.parse_args(sys.argv[1:2])

if args.command == "Document":

    parser = argparse.ArgumentParser(
        prog="{} {}".format(parser.prog, "InfoGain Document"),
        description="{}{}".format(parser.description, "Access the functions within the document")
    )

    commands = parser.add_mutually_exclusive_group(required=True)

    commands.add_argument(
        "--annotate",
        nargs=2,
        metavar=("OntologyPath", "DocumentPath"),
        help="Annotate a document acording to an ontology."
    )

    commands.add_argument(
        "--score",
        nargs=2,
        metavar=("OntologyPath", "DocumentPath"),
        help="Produce metric results for a document, according to an ontology"
    )

    args = parser.parse_args(sys.argv[2:])

    if args.annotate:
        from . import artefact
        from . import knowledge

        artefact.annotate(
            knowledge.Ontology(filepath=args.annotate[0]),
            artefact.Document(filepath=args.annotate[1])
        )

    elif args.score:
        from . import artefact
        from . import knowledge

        artefact.score(
            knowledge.Ontology(filepath=args.annotate[0]),
            artefact.Document(filepath=args.annotate[1]),
            True
        )