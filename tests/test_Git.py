import os
import shutil
import subprocess
import pytest

from atudomain.git.repository import Git
from atudomain.git.repository import NoCommitsError
from tests import SANDBOX_DIR


os.makedirs(SANDBOX_DIR, exist_ok=True)


def test_empty_repo1():
    repo_dir = os.path.join(SANDBOX_DIR, "repo1")
    if os.path.isdir(f"{repo_dir}"):
        shutil.rmtree(f"{repo_dir}")
    subprocess.run(f"git init {repo_dir}", shell=True)
    git = Git(repo_dir)
    with pytest.raises(NoCommitsError):
        git.get_commits()
    git.get_branches()
    shutil.rmtree(f"{repo_dir}")


def test_empty_bare_repo2():
    repo_dir = os.path.join(SANDBOX_DIR, "repo2")
    if os.path.isdir(f"{repo_dir}"):
        shutil.rmtree(f"{repo_dir}")
    subprocess.run(f"git init {repo_dir}", shell=True)
    git = Git(repo_dir)
    with pytest.raises(NoCommitsError):
        git.get_commits()
    git.get_branches()
    shutil.rmtree(f"{repo_dir}")


def test_repo3():
    repo_dir = os.path.join(SANDBOX_DIR, "repo3")
    if os.path.isdir(f"{repo_dir}"):
        shutil.rmtree(f"{repo_dir}")
    subprocess.run(f"git init {repo_dir}", shell=True)
    subprocess.run(f"git echo 'test' > testfile", shell=True, cwd=repo_dir)
    subprocess.run(f"git add .", shell=True, cwd=repo_dir)
    subprocess.run(f"git commit -m 'test'", shell=True, cwd=repo_dir)
    git = Git(repo_dir)
    git.get_commits()
    git.get_branches()
    shutil.rmtree(f"{repo_dir}")
