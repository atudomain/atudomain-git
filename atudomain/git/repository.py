#!/usr/bin/env python3

import re
import subprocess

from atudomain.git.objects import Commit
from atudomain.git.parsers import GitBranchParser
from atudomain.git.parsers import GitLogParser

from typing import List


class Git:
    """
    Represents git repository. Can be used to extract Commits and examine branches.
    It can also be used to conveniently run git commands and get their output.

    :param directory: Path to git repository or bare repository.
    :type directory: str
    :param executable_directory: Path to directory with git binary.
    :type executable_directory: str
    """
    def __init__(
            self,
            directory: str,
            executable_directory=""
    ):
        self._executable_directory = executable_directory
        self._directory = None
        self._build_directory(
            directory=directory
        )
        self._git_log_parser = GitLogParser()
        self._git_branch_parser = GitBranchParser()

    def _build_directory(
            self,
            directory: str
    ) -> None:
        self._directory = directory
        if self._run(["rev-parse", "--git-dir"], check=False).returncode != 0:
            raise NotARepositoryError(directory)

    def _run(
            self,
            command: List[str],
            check=True
    ) -> subprocess.CompletedProcess:
        """
        Runs commands and gets their output.

        :param command: Command to run.
        :type command: List[str]
        :param check: True if exception should be raised when command return code is not 0.
        :type check: bool
        :return: Result of subprocess.run() execution.
        :rtype: subprocess.CompletedProcess
        """
        path = None
        env = None
        if self._executable_directory != "":
            path = self._executable_directory + ":PATH"
        if path:
            env = {"PATH": path}
        try:
            return subprocess.run(
                ["git"] + command,
                check=check,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                shell=False,
                env=env,
                cwd=self._directory
            )
        except subprocess.CalledProcessError as error:
            print(error.stderr)
            raise

    def get_commits(
            self,
            revision_range=""
    ) -> List[Commit]:
        """
        Extracts commits from git 'log --pretty=raw' command, creates Commit objects from them
        and appends them to a list.

        :param revision_range: Any revision range that could be used with git log command.
        :type revision_range: str
        :return: List of Commit objects extracted.
        :rtype: List[Commit]
        """
        if revision_range:
            command = ["log", revision_range, "--pretty=raw"]
        else:
            command = ["log", "--pretty=raw"]
        completed_process = self._run(command, check=False)
        if completed_process.returncode == 128:
            raise NoCommitsError(completed_process.stderr)
        return self._git_log_parser.extract_commits(completed_process.stdout)

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
            self._run(["branch", "--all"]).stdout
        )
        if include is not None:
            branches = [x for x in branches if re.search(include, x)]
        if exclude is not None:
            branches = [x for x in branches if not re.search(exclude, x)]
        return branches

    def add_files(
            self,
            pathspec: str
    ):
        """
        Adds files to stash.

        :param pathspec: Git-add-compatible single-word expression.
        :type pathspec: str
        """
        self._run(["add", pathspec])

    def commit(
            self,
            message: str
    ):
        """
        Creates a commit in a non-interactive way.

        :param message: Commit message.
        :type message: str
        """
        self._run(["commit", "-m", message])

    def pull(
            self
    ):
        """
        Equivalent of 'git pull' without arguments.
        """
        self._run(["pull"])

    def push(
            self,
            remote="origin",
            branch="",
            set_upstream=False
    ):
        """
        Pushes to specific branch in specific remote.

        :param remote: Name of remote.
        :type remote: str
        :param branch: Name of branch.
        :type branch: str
        :param set_upstream: If specified branch should become upstream.
        :type set_upstream: bool
        """
        if branch:
            command = ["push", remote, branch]
        else:
            command = ["push", remote]
        if set_upstream:
            command.append("--set-upstream")
        self._run(command)

    def checkout(
            self,
            target: str
    ):
        """
        Checkouts to specified target.

        :param target: Branch, commit or other target.
        :type target: str
        """
        self._run(["checkout", target])

    def checkout_new_branch(
            self,
            branch: str
    ):
        """
        Creates new branch and checkouts to it.

        :param branch: Name of branch.
        :type branch: str
        """
        self._run(["checkout", "-b", branch])

    def config(
            self,
            name: str,
            value: str
    ):
        """
        Changes git config values in current repository.

        :param name: Name of entry to change.
        :type name: str
        :param value: New value for entry.
        :type value: str
        """
        self._run(["config", name, value])


class NotARepositoryError(Exception):
    pass


class NoCommitsError(Exception):
    pass
