import os

from .document import Document
from .entity import Entity
from .annotation import Annotation
from ..serialisers import SerialiserFactory

class Annotator:

    _AnnotationMapper = {
        Annotation.POSITIVE: '+',
        Annotation.INSUFFICIENT: '~',
        Annotation.NEGATIVE: '-'
    }

    def __init__(self, filepath):

        self._filepath = filepath

        with open(self._filepath, 'r') as fh:
            self._document = Document(content=fh.read())

    def serve(self):

        for sentence in self._document.sentences():
            os.system('cls' if os.name=='nt' else 'clear')

            words = sentence.split()
            indexes = [0] + [i + 1 for i, c in enumerate(sentence) if c == ' ']
            entities = {}
            annotations = []

            while True:
                try:
                    self._drawState(sentence, indexes, entities, annotations)
                    command = input('command: ').lower()
                    if not command:
                        os.system('cls' if os.name=='nt' else 'clear')
                        continue

                    if command in ('e', 'entity'):
                        self._entity(words, indexes, entities)

                    elif command in ('a', 'annotate'):
                        annotations.append(self._annotate(entities))

                    elif command in ('r', 'remove'):
                        self._remove(entities, annotations)

                    elif command in ('n', 'next'):
                        break

                    elif command == 'exit':
                        exit()

                    else:
                        print("Unrecognised command")
                        continue

                    os.system('cls' if os.name=='nt' else 'clear')
                except Exception as e:
                    print("Error on command: {}".format(e))

                except KeyboardInterrupt:
                    os.system('cls' if os.name=='nt' else 'clear')

    def _drawState(self, sentence, indexes, entities, annotations):
        # Generate the initial index str that shows the index of the beginning of the words
        indexesStr = ''
        for index in indexes:
            indexesStr += ' '*(index - len(indexesStr)) + str(index)

        entityStr = ''
        for index, e in sorted(entities.items()):
            name = e.classType[:min(len(e.classType), len(e.surfaceForm))]
            entityStr += ' '*(index - len(entityStr)) + name

        annStr = ''
        for e, ((i, I), ann) in enumerate(annotations):
            annStr += '{4}{0}*{1:{2}^{3}}*\n'.format(
                ' '*(i + len(entities[i].surfaceForm)//2 - 1),
                ann.name,
                self._AnnotationMapper[ann.classification],
                (I + len(entities[I].surfaceForm)//2) - (i + len(entities[i].surfaceForm)//2),
                e
            )

        print(
            "\n"
            "{}"
            "{}\n"
            "{}\n"
            "{}\n".format(annStr, entityStr, indexesStr, sentence)
        )

    def _entity(self, words: str, indexes: [int], entities: dict):

        # Read entity index
        while True:
            try:
                index = int(input('Entity index: '))
                i = indexes.index(index)
                break

            except Exception as e:
                print('Error while reading index: {}'.format(e))

        # Read entity class
        while True:
            try:
                entity_class = input('Entity Class: ')
                break

            except Exception as e:
                print('Error: {}'.format(e))

        # Read entity class
        while True:
            try:
                confidence = float(input('Entity confidence (leave blank for 1.): ') or '1')
                assert 0. <= confidence and confidence <= 1.
                break

            except Exception as e:
                print('Error: {}'.format(e))

        e = Entity(entity_class, words[i], confidence)

        if index in entities:
            self._document.entities.remove(entities)

        self._document.entities.add(e, index)
        entities[index] = e

    def _annotate(self, entities):

        # Read entity index
        while True:
            try:
                di = int(input('Domain index: '))
                domain = entities[di]
                break

            except Exception as e:
                print('Error while reading domain index: {}'.format(e))

        # Read entity index
        while True:
            try:
                ti = int(input('Target index: '))
                target = entities[ti]
                break

            except Exception as e:
                print('Error while reading range index: {}'.format(e))

        # Read entity index
        while True:
            try:
                name = input('Relation name: ')
                break

            except Exception as e:
                print('Error while reading domain index: {}'.format(e))

        # Read entity index
        while True:
            try:
                classification = int(input('Classification (leave blank for 1) [1, 0, -1]: ') or 1)
                assert classification in (1, 0, -1)
                break

            except Exception as e:
                print('Error while reading domain index: {}'.format(e))

        annotation = Annotation(domain, name, target, classification=classification)
        self._document.annotations.add(annotation)
        return tuple(sorted((di, ti))), annotation

    def _remove(self, entities, annotations):

        # Read entity index
        while True:
            try:
                _type = input('Artefact (e/a): ').lower()
                assert _type in ('e', 'entity', 'a', 'annotate')
                break

            except Exception as e:
                print('Error on type selection: {}'.format(e))

        # Read entity index
        while True:
            try:
                index = int(input('index: '))
                break

            except Exception as e:
                print('Error while reading domain index: {}'.format(e))

        if _type in ('e', 'entity'):
            entity = entities[index]
            self._document.entities.remove(entity)
            del (entities[index])

        else:
            _, ann =  annotations[index]
            self._document.annotations.remove(ann)
            del annotations[index]

    def save(self):
        SerialiserFactory('json', Document).save(self._document, self._filepath + '.dig')
