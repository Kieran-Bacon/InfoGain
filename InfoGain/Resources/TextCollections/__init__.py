import os

ROOT = os.path.dirname(os.path.abspath(__file__))

COLLECTIONS = []

for name in os.listdir(ROOT):
    if name == "__init__.py": continue
    filepath = os.path.join(ROOT, name)
    if os.path.isdir(filepath): continue

    COLLECTIONS.append(filepath)