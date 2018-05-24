import InfoGain
from InfoGain.Resources import Language

ext = InfoGain.RelationExtractor(ontology=Language.ontology())

natasa = InfoGain.Concept("Natasa")
natasa.addParent(ext.concept("Person"))
ext.addConcept(natasa)

ext.fit(Language.training())
print("Training concluded\n\n")


documents = ext.predict(Language.testing() + [InfoGain.Document(content="Natasa has been learning to speak English. Kieran cannot speak English")])

for document in documents:
    print(document.text())

    for segment in document.datapoints():
        for point in segment:
            print(point.text, "\n", point,"\n\n")

    print("\n\n")