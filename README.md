# Simple Python wrapper for Git
[![pipeline](https://gitlab.com/atudomain/atudomain-git/badges/master/pipeline.svg)](https://gitlab.com/atudomain/atudomain-git/-/tree/master)
[![Documentation Status](https://readthedocs.org/projects/atudomain-git/badge/?version=latest)](https://atudomain-git.readthedocs.io/en/latest/?badge=latest)

Provides access to Commit objects and easy branch listing.

- License: 3-Clause BSD
- Python: Python 3.6+

## Table of Contents
- [Installation](#installation)
- [Quickstart](#quickstart)
    - [Getting Branches](#getting-branches)
    - [Getting Commits](#getting-commits)
    - [Getting Commit details](#getting-commit-details)
- [API Documentation](#api-documentation)

## Installation

Install using pip:
```bash
python3 -m pip install atudomain-git --user 
```

Alternatively, you can just append downloaded repository path to PYTHONPATH.

## Quickstart

Import Git class:
```python
from atudomain.git import Git
```

Create Git object:
```python
git = Git('/home/user/example-repo')
```

### Getting branches
Get list of remote origin branches:
```python
branches = git.get_branches(include='^remotes/origin')
```

Get list of local branches:
```python
branches = git.get_branches(exclude='^remotes/')
```

### Getting Commits
Get list of Commits for the current branch:
```python
commits = git.get_commits()
```

Get list with last Commit for the current branch:
```python
commits = git.get_commits('HEAD^..HEAD')
```

### Getting Commit details
Get committer date from Commit:
```python
committer_date = commits[0].committer_date
```

Get commit id from Commit:
```python
commit_id = commits[0].commit_id
```

Check if Commit is a merge:
```python
is_merge = commits[0].is_merge
```

## API Documentation
https://atudomain-git.readthedocs.io/en/latest/
