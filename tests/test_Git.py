import os
import shutil
import subprocess
import pytest

from atudomain.git.repository import Git
from atudomain.git.repository import NoCommitsError
from tests import SANDBOX_DIR


os.makedirs(SANDBOX_DIR, exist_ok=True)

def test_empty_repo():
    repo_dir = os.path.join(SANDBOX_DIR, "repo")
    if os.path.isdir(f"{repo_dir}"):
        shutil.rmtree(f"{repo_dir}")
    subprocess.run(f"git init {repo_dir}", shell=True)
    git = Git(os.path.join(SANDBOX_DIR, "repo"))
    with pytest.raises(NoCommitsError):
        git.get_commits()
    git.get_branches()
    shutil.rmtree(f"{repo_dir}")

def test_empty_bare_repo():
    repo_dir = os.path.join(SANDBOX_DIR, "repo")
    if os.path.isdir(f"{repo_dir}"):
        shutil.rmtree(f"{repo_dir}")
    subprocess.run(f"git init {repo_dir}", shell=True)
    git = Git(os.path.join(SANDBOX_DIR, "repo"))
    with pytest.raises(NoCommitsError):
        git.get_commits()
    git.get_branches()
    shutil.rmtree(f"{repo_dir}")
