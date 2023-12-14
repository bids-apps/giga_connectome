# Contribution

## Setting up your environment for development

1. Fork the repository from github and clone your fork locally

```bash
git clone git@github.com:<your_username>/giga_connectome.git
```

2. Set up a virtual environment to work in using whichever environment management tool you're used to and activate it. For example:

```bash
python3 -m venv giga_connectome
source giga_connectome/bin/activate
```

3. Install the developmental version of the project. This will include all the dependency necessary for developers. For details on the packages installed, see `pyproject.toml`.

```bash
pip install -e .[dev]
```

4. Install pre-commit hooks to run all the checks before each commit.

```bash
pre-commit install
```

## Contributing to code

This is a very generic workflow.

1. Comment on an existing issue or open a new issue referencing your addition.

:::{tip}
Review and discussion on new code can begin well before the work is complete, and the more discussion the better!
The development team may prefer a different path than you've outlined, so it's better to discuss it and get approval at the early stage of your work.
:::

2. On your fork, create a new branch from main:

```bash
git checkout -b your_branch
```

3. Make the changes, lint, and format.

4. Commit your changes on this branch.

5. Run the tests locally; you can run spectfic tests to speed up the process:

```bash
pytest -v giga_connectome/tests/tests/test_connectome.py::test_calculate_intranetwork_correlation
```

6. push your changes to your online fork. If this is the first commit, you might want to set up the remote tracking:

```bash
git push origin HEAD --set-upstream
```
In the future you can simply do:

```bash
git push
```
7. Submit a pull request from your fork of the repository.

8. Check that all continuous integration tests pass.

## Contributing to documentation

The workflow is the same as code contributions, with some minor differences.

1. Install the `[doc]` dependencies.

```bash
pip install -e '.[doc]'
```

2. After making changes, build the docs locally:

```bash
cd docs
make html
```

3. Submit your changes.

## Writing a PR

When opening a pull request, please use one of the following prefixes:

- **[ENH]** for enhancements
- **[FIX]** for bug fixes
- **[TEST]** for new or updated tests
- **[DOCS]** for new or updated documentation
- **[STYL]** for stylistic changes
- **[MAINT]** for refactoring existing code, any maintainace related things

Pull requests should be submitted early and often (please don't mix too many unrelated changes within one PR)!
If your pull request is not yet ready to be merged, please submit as a drafted PR.
This tells the development team that your pull request is a "work-in-progress", and that you plan to continue working on it.

One your PR is ready a member of the development team will review your changes to confirm that they can be merged into the main codebase.

## Making a release

Currently this project is not pushed to PyPi.
We simply tag the version on the repository so users can reference the version of installation.
You need to be a administrator of the upstream repository (`SIMEXP/giga_connectome`) to do this.

```bash
git checkout main
git pull upstream main
git tag -a x.y.z -m "Some descriptions"
git push upstream --tags
```

Afterwards, please build the docker container and push to docker hub:

```bash
docker login -u haotingwang
docker build . --file Dockerfile --tag haotingwang/giga_connectome:x.y.z
docker push haotingwang/giga_connectome
```
Before any further discussion, this will be pushed to HTW's docker hub.

Based on contributing guidelines from the [STEMMRoleModels](https://github.com/KirstieJane/STEMMRoleModels/blob/gh-pages/CONTRIBUTING.md) project and [Nilearn contribution guidelines](https://nilearn.github.io/stable/development.html).
