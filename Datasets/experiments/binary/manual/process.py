import os, re

from InfoGain import *

# Load an the dataset's ontology
ontology = Ontology(filepath="datasetont.json")

# Convert the dev files into processable files
if False:
    for file in os.listdir("./dev"):
        if "processed" in file: continue

        processed_content = []

        with open(os.path.join("./dev",file)) as handler:
            # Read the content
            content = handler.read().splitlines()[1:]

            for parts in content:
                line = parts.split("\t")[-1]

                # Clean the line
                line = re.sub("--->|<---|{{{|}}}","",line)

                # Replace concepts
                while True:
                    match = re.search("\[\[\[[\w \S][^\]]+\]\]\]", line)
                    if match is None: break
                    processed = " ".join(re.sub("\[|\]", "", match.group(0)).split()[1:])
                    line = line[:match.span()[0]] + processed + line[match.span()[1]:]

                processed_content.append(line)

        with open(os.path.join("./dev", "processed-"+file), "w") as handler:
            handler.write(" ".join(processed_content))

# Convert processable file
if True:
    for file in os.listdir("./dev"):
        if not "processed" in file: continue

        Ann = AnnotationDocument(filepath=os.path.join("./dev",file))

        print("Document")

        Ann.annotate(ontology, filename=os.path.join("./dev","Xtr-"+file))