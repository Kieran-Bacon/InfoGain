from InfoGain.Ontology import Ontology
from InfoGain.Documents.Document import Document
from InfoGain.Documents.TrainingDocument import TrainingDocument
import InfoGain.Documents.DocumentOperations as DO

class AnnotationDocument(Document):
    """ Extension on the Document object to allow for the quick and painless 
    annotation of a documents datapoints """

    def annotate(self, ont: Ontology, save: bool = True, filename: str = None) -> TrainingDocument:
        """ Begin the annotation process """

        # Check to see if the document is to be saved
        if save and not filename:
            ans = DO.cmdread("Save the generated training document?", ['Y','N'])
            filename = DO.cmdread("Filename: ") if ans == "Y" else None

        # Process the document according to the ontology
        self.processKnowledge(ont)

        index, total = 0, sum([len(x) for x in self._datapoints])
        annotated = []

        for segment in self.datapoints():
            for point in segment:

                index += 1
                mult = int((index/total)*25)

                print("|" + "#"*mult + "-"*(25-mult) + "|", "({}/{} datapoints)".format(index, total))

                print("TEXT:\n{}\n".format(point.text))

                print("RELATION: {}  {}   {}  {}   {}".format(point.domain, point.domainRepr, point.relation, point.target, point.targetRepr))

                ans = DO.cmdread("Does this string represent this relation?",['-1','0','1'])

                point.annotation = int(ans)
                annotated.append(point)

                print("\n\n\n\n")

        xtr = TrainingDocument(content=self._content)
        xtr.datapoints(annotated)
        
        if filename: xtr.save(filename=filename)

        return xtr
                


