import os, sys, re, unittest

class Test_CodeQuality(unittest.TestCase):

    def setUp(self):

        self.ignore = [
            "__pycache__",
            "artefact/__init__.py",
            "infogain/exceptions.py"
        ]
        self.infogain_location = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "infogain"))
        self.tests_location = os.path.abspath(os.path.dirname(__file__))

    def parse_directory(self, directory):

        issues = []

        printIssue = "Print statement found in {}: line {} \"{}\""
        todoIssue = "TODO statement found in {}: line {} \"{}\""
        passIssue = "Pass statement found in {}: line {} \"{}\""

        for (dirpath, _, filenames) in os.walk(directory):

            for filename in filenames:
                directory = dirpath.split("/")[-1]
                if directory in self.ignore: continue
                if os.path.join(directory, filename) in self.ignore: continue
                if os.path.splitext(filename)[1] != ".py": continue

                try:
                    with open(os.path.join(dirpath, filename), "r") as handler:
                        previous = "BEGINNING OF SENTENCE"
                        for line, content in enumerate(handler):
                            content = re.sub("\n","", content.strip())
                            if re.search(r"print\(.*\)", content):
                                issues.append(printIssue.format(filename, line, content))
                            if re.search(r"#\s*TODO", content):
                                issues.append(todoIssue.format(filename, line, content))
                            if re.search(r"^\s*pass", content):
                                issues.append(passIssue.format(filename, line, previous))
                            previous = content
                except:
                    continue
        
        return issues


    def test_Code_to_be_removed(self):

        issues = self.parse_directory(self.infogain_location)

        if issues:
            self.fail("\n" + "\n".join(issues))

    def test_tests_Code_to_be_removed(self):

        issues = self.parse_directory(self.tests_location)

        if issues:
            self.fail("\n" + "\n".join(issues))