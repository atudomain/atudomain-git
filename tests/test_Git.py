import os
import shutil
import subprocess
import pytest

from atudomain.git.repository import Git
from atudomain.git.repository import NoCommitsError
from tests import SANDBOX_DIR


os.makedirs(SANDBOX_DIR, exist_ok=True)
repo_dir = os.path.join(SANDBOX_DIR, "repo")


def create_repo(is_bare=False):
    if os.path.isdir(f"{repo_dir}"):
        shutil.rmtree(f"{repo_dir}")
    if is_bare:
        subprocess.run(f"git init {repo_dir} --bare", shell=True)
    else:
        subprocess.run(f"git init {repo_dir}", shell=True)


def remove_repo():
    shutil.rmtree(f"{repo_dir}")


def add_commits():
    subprocess.run(f"git echo 'test' > testfile", shell=True, cwd=repo_dir)
    subprocess.run(f"git add .", shell=True, cwd=repo_dir)
    subprocess.run(f"git config user.name Test Example", shell=True, cwd=repo_dir)
    subprocess.run(f"git config user.email test@example.com", shell=True, cwd=repo_dir)
    subprocess.run(f"git commit -m 'test'", shell=True, cwd=repo_dir)


@pytest.fixture
def git():
    create_repo()
    yield Git(repo_dir)
    remove_repo()


@pytest.fixture
def git_bare():
    create_repo(is_bare=True)
    yield Git(repo_dir)
    remove_repo()


@pytest.fixture
def git_with_commits():
    create_repo()
    add_commits()
    yield Git(repo_dir)
    remove_repo()


def test_empty_repo(git):
    with pytest.raises(NoCommitsError):
        git.get_commits()
    git.get_branches()


def test_empty_bare_repo(git_bare):
    with pytest.raises(NoCommitsError):
        git_bare.get_commits()
    git_bare.get_branches()


def test_repo(git_with_commits):
    git_with_commits.get_commits()
    git_with_commits.get_branches()
