#!/usr/bin/python3

import os
import re
import subprocess

from typing import List
from shutil import which
from atudomain.git.exceptions.GitBinaryNotFoundError import GitBinaryNotFoundError
from atudomain.git.parsers.GitLogParser import GitLogParser
from atudomain.git.exceptions.NotARepositoryError import NotARepositoryError


class Git:
    """
    Depends on python 3.5+.
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
        self._binary_path_list = self._build_binary_path_list(
            binary_path=binary_path
        )
        self._directory = self._build_directory(
            directory=directory
        )
        self._git_log_parser = GitLogParser()

    def _build_binary_path_list(
            self,
            binary_path: str
    ) -> List[str]:
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
        return binary_path_list

    @staticmethod
    def _build_directory(
            directory: str
    ) -> str:
        if directory != '/':
            directory = directory.rstrip('/')
        if not os.path.isdir(directory + '/.git'):
            raise NotARepositoryError(directory)
        return directory

    def run(
            self,
            command: str,
            check=True
    ) -> subprocess.CompletedProcess:
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
            revision_range: str
    ):
        return self._git_log_parser.extract_commits(
            self.run(
                'log {revision_range} --pretty=raw'.format(
                    revision_range=revision_range
                )
            ).stdout
        )
