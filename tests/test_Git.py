import unittest

from atudomain.git.Git import Git
from atudomain.git.exceptions.UnclosedQuoteError import UnclosedQuoteError


class GitTest(unittest.TestCase):
    def setUp(self) -> None:
        self.git = Git('.')

    def test_convert_to_subprocess_list(self) -> None:
        command_1 = 'status'
        list_1 = self.git._convert_to_subprocess_list(
            command_1
        )
        self.assertListEqual(['status'], list_1)

        command_2 = 'log HEAD^..HEAD --format=raw'
        list_2 = self.git._convert_to_subprocess_list(
            command_2
        )
        self.assertListEqual([
            'log',
            'HEAD^..HEAD',
            '--format=raw'
        ], list_2)

        with self.assertRaises(UnclosedQuoteError):
            command_3 = 'log "smth'
            list_3 = self.git._convert_to_subprocess_list(
                command_3
            )

        command_4 = 'log "some\'"thing'
        list_4 = self.git._convert_to_subprocess_list(
            command_4
        )
        self.assertListEqual([
            'log',
            'some\'thing'
        ], list_4)

        command_5 = 'log   \t  "some \' \'"thing some\' \'thing thing'
        list_5 = self.git._convert_to_subprocess_list(
            command_5
        )
        self.assertListEqual([
            'log',
            'some \' \'thing',
            'some thing',
            'thing'
        ], list_5)


if __name__ == '__main__':
    unittest.main()
