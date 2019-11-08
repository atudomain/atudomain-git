import os
import unittest

from atudomain.git.parsers.GitBranchParser import GitBranchParser


class GitBranchParserTest(unittest.TestCase):
    SCRIPT_DIR = os.path.dirname(os.path.realpath('__file__'))

    def setUp(self) -> None:
        self.git_branch_parser = GitBranchParser()

    @staticmethod
    def read_branches_string(
            file: str
    ) -> str:
        with open(file, 'r') as f:
            branches_string = f.read()
        return branches_string

    def test_extract_branch_strings(self):
        branches_string_1 = self.read_branches_string(
            file=self.SCRIPT_DIR + '/resources/test__extract_branch_strings_1.txt'
        )

        branch_strings_1 = self.git_branch_parser._extract_branch_strings(
            branches_string=branches_string_1
        )

        self.assertListEqual(
            [
                '  branch/1/2019',
                '  branch/2/2019',
                '  branch/3/2019',
                '* master'
            ],
            branch_strings_1
        )

    def test_extract_branches(self):
        branches_string_1 = self.read_branches_string(
            file=self.SCRIPT_DIR + '/resources/test_extract_branches_1.txt'
        )
        branches = self.git_branch_parser.extract_branches(
            branches_string=branches_string_1
        )
        self.assertListEqual(
            [
                'master',
                'remotes/origin/master'
            ],
            branches
        )


if __name__ == '__main__':
    unittest.main()
