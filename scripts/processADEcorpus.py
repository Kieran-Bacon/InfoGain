import InfoGain

medicine = InfoGain.Ontology(filepath="ADE_corpus.ont")
trainingDocuments = [InfoGain.ADEDocument(medicine,"DRUG-AE.rel"), InfoGain.ADEDocument(medicine,"DRUG-DOSE.rel")]


print(medicine.concept("Drug"))