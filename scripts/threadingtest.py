import InfoGain

ont = InfoGain.Resources.Language.ontology()

InfoGain.AnnotationDocument(filepath="./tobeannotated.txt").annotate(ont)