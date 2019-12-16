import os
import sys
import argparse

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
        nargs=1,
        metavar=("document_path"),
        help="Annotate a document according to an ontology."
    )

    commands.add_argument(
        "--score",
        nargs=2,
        metavar=("document_path", "extractor_path"),
        help="Produce metric results for a document, according to an ontology"
    )

    args = parser.parse_args(sys.argv[2:])

    if args.annotate:
        from .artefact.annotator import Annotator

        annotator = Annotator(args.annotate[0])
        annotator.serve()
        annotator.save()

    elif args.score:
        print('hello')