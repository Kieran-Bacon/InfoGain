import sys

help_text = """
    annotate
    $ annotate (Ontology Path) (Document Path) (Document Path)...
"""

if len(sys.argv) == 1:
    print(help_text)

for i in range(1, len(sys.argv)):

    if sys.argv[i] == "annotate":
        if i+2 >= len(sys.argv):
            print("Annotation requires ontology path and document path requires filepath")
            break

        from .Documents import annotate, Document
        from .Knowledge import Ontology

        annotate(Ontology(filepath=sys.argv[i+1]), Document(filepath=sys.argv[i+2]), save=True)

        break

    if sys.argv[i] == "-h":
        print(help_text)
        break

