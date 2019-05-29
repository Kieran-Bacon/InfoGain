import os
from setuptools import setup, find_packages

with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "README.md")), "r") as handler:
      README = handler.read()
requires = ["sklearn", "matplotlib", "gensim", "mock", "tqdm"]

setup(name='infogain',
      install_requires=requires,
      version="1.0.1",
      description="Information Extraction and Generation",
      long_description=README,
      long_description_content_type="text/markdown",

      author="Kieran Bacon",
      author_email="Kieran.Bacon@outlook.com",
      url="https://github.com/Kieran-Bacon/InfoGain",

      packages=find_packages(),
      package_data={"": ["*.txt", "*.json"]},
      include_package_data=True
)