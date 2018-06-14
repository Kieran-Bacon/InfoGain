from InfoGain.Documents import Document
from InfoGain.Extraction import RelationExtractor
from InfoGain.Documents.Models import SpellingModel

extractor = RelationExtractor.load("./RelationExtractor")

document = Document(content="Luke can speak English rather well")
extractor.predict(document)

for point in document.datapoints():
    print(point)