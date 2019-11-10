#!/usr/bin/python3

import os
import re
import subprocess

from typing import List
from shutil import which

from atudomain.git.Commit import Commit
from atudomain.git.exceptions.GitBinaryNotFoundError import GitBinaryNotFoundError
from atudomain.git.exceptions.UnclosedQuoteError import UnclosedQuoteError
from atudomain.git.parsers.GitBranchParser import GitBranchParser
from atudomain.git.parsers.GitLogParser import GitLogParser
from atudomain.git.exceptions.NotARepositoryError import NotARepositoryError


class Git:
    """
    Represents git repository. Can be used to extract Commits and examine branches.
    It can also be used to conveniently run git commands and get their output.

    :param directory: Path to git repository or bare repository.
    :type directory: str
    :param binary_path: Path to directory with git binary.
    :type binary_path: str
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

    @staticmethod
    def _convert_to_subprocess_list(
            command: str
    ) -> List[str]:
        """
        This method was necessary to allow quoting whitespace and other symbols in git commands.

        :param command: String command passed to run() method.
        :type command: str
        :return: List of strings for subprocess.run().
        :rtype: List[str]
        """
        last_quote = None
        command_list = list()
        list_element = ''
        for symbol in command:
            if re.match(r'(\'|\")', symbol) and not last_quote:
                last_quote = re.match(r'(\'|\")', symbol).group(1)
                continue
            if re.match(r'(\'|\")', symbol) \
                    and last_quote \
                    and re.match(r'(\'|\")', symbol).group(1) == last_quote:
                last_quote = None
                continue
            if last_quote:
                list_element += symbol
            else:
                if re.match(r'\s', symbol):
                    command_list.append(list_element)
                    list_element = ''
                else:
                    list_element += symbol
        if last_quote:
            raise UnclosedQuoteError(command)
        command_list.append(list_element)
        return [x for x in command_list if x]

    def run(
            self,
            command: str,
            check=True
    ) -> subprocess.CompletedProcess:
        """
        Runs git commands and gets their output.

        :param command: Command to run without 'git' and repository location part ie. 'branch -v'.
        :type command: str
        :param check: True if exception should be raised when command return code is not 0.
        :type check: bool
        :return: Result of subprocess.run() execution.
        :rtype: subprocess.CompletedProcess
        """
        command_list = self._convert_to_subprocess_list(
            command=command
        )
        try:
            return subprocess.run(
                [
                    'git',
                    '-C',
                    self._directory
                ] + command_list,
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
        Extracts commits from git 'log --pretty=raw' command, creates Commit objects from them
        and appends them to a list.

        :param revision_range: Any revision range that could be used with git log command.
        :type revision_range: str
        :return: List of Commit objects extracted.
        :rtype: List[Commit]
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
        Extracts branch names from 'git branch --all' command and appends them to a list.
        Skips redundant information such as current branch pointer ('*') or relations ('->').

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
