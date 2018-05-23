import InfoGain
from InfoGain.Resources import Language

Language.ontology()
Language.getTraining()
Language.getTesting()

ext = InfoGain.RelationExtractor(ontology=Language.ontology())

ext.fit(Language.getTraining())

print(ext.predict([d for d in Language.getTesting()]))