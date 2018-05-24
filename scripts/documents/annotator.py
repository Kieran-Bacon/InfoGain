import InfoGain

ont = InfoGain.Resources.Language.ontology()

InfoGain.AnnotationDocument(filepath="./test.txt").annotate(ont, filename="annotated-Speaks.json")