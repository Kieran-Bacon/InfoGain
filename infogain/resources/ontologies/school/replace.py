import os
import json

from infogain.artefact import Document, Entity, Annotation
from infogain import Serialiser

for filename in os.listdir("./training"):
    if filename == "__init__.py": continue

    with open(os.path.join("./training", filename)) as handle:
        data = json.load(handle)

    index = 0
    content = ""
    entities = []
    annotations = []
    for datapoint in data['datapoints']:

        # Process the content
        text = Document(datapoint['text']).content

        domain = Entity(datapoint['domain']['concept'], datapoint['domain']['text'])
        target = Entity(datapoint['target']['concept'], datapoint['target']['text'])

        entities.append((domain, index + text.find(domain.surfaceForm)))
        entities.append((target, index + text.find(target.surfaceForm)))

        annotations.append(Annotation(domain, datapoint['relation'], target, annotation=datapoint['annotation']*10))

        content += text
        index += len(text)

    document = Document(content, processed=True)
    for e in entities: document.entities.add(*e)
    for a in annotations: document.annotations.add(a)

    Serialiser('json', Document).save(document, os.path.join("./training", filename))

