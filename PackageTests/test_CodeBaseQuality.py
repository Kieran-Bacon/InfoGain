import os, sys, re, unittest

class Test_CodeQuality(unittest.TestCase):

    def setUp(self):

        self.ignore = [
            "__pycache__",
            "artefact/__init__.py",
            "infogain/exceptions.py",
            "PackageTests/test_CodeBaseQuality.py"
        ]
        self.infogain_location = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "infogain"))
        self.tests_location = os.path.abspath(os.path.dirname(__file__))

    def parse_directory(self, directory):

        issues = []

        printIssue = "Print statement found in {}/{}: line {} \"{}\""
        todoIssue = "TODO statement found in {}/{}: line {} \"{}\""
        passIssue = "Pass statement found in {}/{}: line {} \"{}\""
        lengthIssue = "Line length exceeded in {}/{}: line {} length {} \"{}\""

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
                            line += 1  # Increase the index to match line number
                            content = re.sub("\n", "", content)  # Remove newline character only, keep other white space

                            # Check if the number of characters in the line exceeds the limit
                            if len(content) > 120:
                                issues.append(
                                    lengthIssue.format(
                                        directory,
                                        filename,
                                        line,
                                        len(content),
                                        content.strip()[:80] + "...")
                                )

                            content = content.strip()

                            # Check if the line contains a print statement
                            if re.search(r"print\(.*\)", content):
                                issues.append(printIssue.format(directory, filename, line, content))

                            # Check if the line contains an todo
                            if re.search(r"#\s*TODO", content):
                                issues.append(todoIssue.format(directory, filename, line, content))

                            # Check if the line is a pass statement on a difinition (aka not in a try except situation)
                            if re.search(r"^\s*pass(?!\s)", content) and previous.strip() != "except:":
                                issues.append(passIssue.format(directory, filename, line, previous))

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