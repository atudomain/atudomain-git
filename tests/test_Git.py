import os
import shutil
import subprocess
import pytest

from atudomain.git.repository import Git
from atudomain.git.repository import NoCommitsError
from tests import SANDBOX_DIR


os.makedirs(SANDBOX_DIR, exist_ok=True)
repo_dir = os.path.join(SANDBOX_DIR, "repo")
clone_repo_dir = os.path.join(SANDBOX_DIR, "clone_repo")


def create_repo(is_bare=False):
    if os.path.isdir(f"{repo_dir}"):
        shutil.rmtree(f"{repo_dir}")
    if is_bare:
        subprocess.run(f"git init {repo_dir} --bare", shell=True)
    else:
        subprocess.run(f"git init {repo_dir}", shell=True)


def clone_repo():
    if os.path.isdir(f"{clone_repo_dir}"):
        shutil.rmtree(f"{clone_repo_dir}")
    else:
        subprocess.run(f"git clone {repo_dir} {clone_repo_dir}", shell=True)


def remove_repo():
    shutil.rmtree(f"{repo_dir}")


def remove_clone():
    shutil.rmtree(f"{clone_repo_dir}")


def add_commits():
    subprocess.run(f"echo 'test' > testfile", shell=True, cwd=repo_dir)
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


@pytest.fixture
def git_with_origin():
    create_repo()
    clone_repo()
    add_commits()
    yield Git(clone_repo_dir)
    remove_repo()
    remove_clone()


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


def test_create_commit_and_get_commits(git):
    subprocess.run(f"echo 'test create' > test_create.txt", shell=True, cwd=repo_dir)
    git.config("user.name", "Test Example")
    git.config("user.email", "test@example.com")
    git.add_files("test_create.txt")
    git.commit("test create")
    assert "test create" in git.get_commits("HEAD")[0].message


def test_pull(git_with_origin):
    git_with_origin.pull()
