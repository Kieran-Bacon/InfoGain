import InfoGain

ontology = InfoGain.Ontology(filepath="./datasetont.json")

document = InfoGain.Document(filepath="./dev/nytimes-exemplar.txt")

document.processKnowledge(ontology)

document.save()