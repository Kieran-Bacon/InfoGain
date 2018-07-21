#!/usr/bin/python

import sys
import re

totalgt = 0
totalSystem = 0
correct = 0

def entityContained(entity, entities):
    for e in entities:
        if e.endswith(entity):
            return True
    return False

with open(sys.argv[1]) as gt, open(sys.argv[2]) as so:
    for gtline in gt:
        totalgt += len([m.start() for m in re.finditer('\[\[\[', gtline)])
        entities = [m.lower() for m in re.findall(r'\[\[\[\w+? (.+?)\]\]\]', gtline)]
        gtrelation = re.search('\{\{\{(.+)\}\}\}', gtline).group(1)
        
        soline = so.readline()
        soarray = soline.split('\t')
        relation = soarray[0]
        args = soarray[1]
        if args != "---":
            for arg in args.split(',,'):
                totalSystem += 1
                if entityContained(arg.lower(), entities):
                    correct += 1
        
        
print "Total Ground Truth: " + str(totalgt)
print "Total System: " + str(totalSystem)
print "Correct: " + str(correct)
print "Precision: " + str(correct/float(totalSystem))
print "Recall: " + str(correct/float(totalgt))
