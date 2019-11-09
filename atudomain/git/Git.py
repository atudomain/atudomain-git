#!/usr/bin/python3

import os
import re
import subprocess

from typing import List
from shutil import which

from atudomain.git.Commit import Commit
from atudomain.git.exceptions.GitBinaryNotFoundError import GitBinaryNotFoundError
from atudomain.git.parsers.GitBranchParser import GitBranchParser
from atudomain.git.parsers.GitLogParser import GitLogParser
from atudomain.git.exceptions.NotARepositoryError import NotARepositoryError


class Git:
    """
    Represents git repository. Can be used to extract Commits and examine branches.
    It can also be used to conveniently run git commands and get their output.
    """
    COMMON_BINARY_PATHS = [
        '/bin',
        '/usr/bin'
    ]

    def __init__(
            self,
            directory: str,
            binary_path=''
    ):
        self._binary_path_list = None
        self._build_binary_path_list(
            binary_path=binary_path
        )
        self._directory = None
        self._build_directory(
            directory=directory
        )
        self._git_log_parser = GitLogParser()
        self._git_branch_parser = GitBranchParser()

    def _build_binary_path_list(
            self,
            binary_path: str
    ) -> None:
        binary_path_list = self.COMMON_BINARY_PATHS
        if binary_path:
            if not os.path.isdir(binary_path):
                raise NotADirectoryError(binary_path)
            self._binary_path_list.insert(
                index=0,
                object=binary_path
            )
        binary_shell_independent = False
        for binary_path in binary_path_list:
            if os.path.isfile(
                    binary_path.rstrip('/') + '/git'
            ):
                binary_shell_independent = True
                break
        if not binary_shell_independent:
            if which('git') is None:
                raise GitBinaryNotFoundError()
            else:
                print("WARNING: git binary depends on current environment variables!")
        self._binary_path_list = binary_path_list

    def _build_directory(
            self,
            directory: str
    ) -> None:
        if directory != '/':
            directory = directory.rstrip('/')
        self._directory = directory
        if self.run('rev-parse --git-dir', check=False).returncode != 0:
            raise NotARepositoryError(directory)

    def run(
            self,
            command: str,
            check=True
    ) -> subprocess.CompletedProcess:
        """
        Runs git commands and gets their output.

        Examples:
        stdout_string = git.run('branch -v').stdout
        return_code = git.run('status', check=False).returncode
        stderr_string = git.run('branch -v', check=False).stderr

        :param command: Command to run without 'git' and repository location part ie. 'branch -v'.
        :type command: str
        :param check: True if exception should be raised when command return code is not 0.
        :type check: bool
        :return: Result of subprocess.run() execution.
        :rtype subprocess.CompletedProcess
        """
        command = re.split(r'\s+', command.strip())
        try:
            return subprocess.run(
                [
                    'git',
                    '-C',
                    self._directory
                ] + command,
                check=check,
                capture_output=True,
                universal_newlines=True,
                env={'PATH': ':'.join(self._binary_path_list)}
            )
        except subprocess.CalledProcessError as error:
            print(error.stderr)
            raise

    def get_commits(
            self,
            revision_range=''
    ) -> List[Commit]:
        """
        Extracts commits from git log --pretty=raw command, creates Commit objects from them
        and appends them to a list.

        Examples:
        commits_1 = git.get_commits()
        commits_2 = git.get_commits('HEAD^..HEAD')

        :param revision_range: Any revision range that could be used with git log command.
        :type revision_range: str
        :return: List of Commit objects extracted.
        :rtype List[Commit]
        """
        return self._git_log_parser.extract_commits(
            self.run(
                'log {revision_range} --pretty=raw'.format(
                    revision_range=revision_range
                )
            ).stdout
        )

    def get_branches(
            self,
            include=None,
            exclude=None
    ) -> List[str]:
        """
        Extracts branch names from git branch --all command and appends them to a list.
        Skips redundant information such as current branch pointer ('*') or relations ('->').

        Examples:

        :param include: Regex (re module) to include branch names in list. None means all.
        :type include: str
        :param exclude: Regex (re module) to exclude branch names from list.
        :type exclude: str
        :return: List of branch names.
        :rtype: List[str]
        """
        branches = self._git_branch_parser.extract_branches(
            self.run('branch --all').stdout
        )
        if include is not None:
            branches = [x for x in branches if re.search(include, x)]
        if exclude is not None:
            branches = [x for x in branches if not re.search(exclude, x)]
        return branches

