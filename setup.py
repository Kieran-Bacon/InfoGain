from setuptools import setup, find_packages

with open("README.md", "r") as handler:
      README = handler.read()
requires = ["sklearn", "matplotlib", "gensim", "mock"]

setup(name='InfoGain',
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
