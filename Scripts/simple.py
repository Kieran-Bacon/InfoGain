from InfoGain import Ontology, RelationExtractor

languages = Ontology("Languages", "./languages.json")

LanguageExtractor = RelationExtractor(languages)