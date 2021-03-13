import unittest

from atudomain.git.Git import Git


def test_readonly_methods() -> None:
    git = Git('.')
    git.get_commits()
    git.get_branches()
