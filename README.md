[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

---

# aliquot-level-maf
Library to process aliquot-level MAF files.

This library requires Python 3.6+.

- [aliquot-level-maf](#aliquot-level-maf)
  - [Set up](#set-up)
  - [Dependencies](#dependencies)
    - [Installing dependencies](#installing-dependencies)
    - [Adding dependencies](#adding-dependencies)
  - [Tests](#tests)

## Set up

This repository makes use of `pre-commit` for code formatting, linting
and secrets detecting.  In order to make use of it, you must run the following
commands to install `pre-commit`.
```
pip install -r dev-requirements.txt
pre-commit install
```

## Dependencies

### Installing dependencies

```
pip install -r dev-requirements.txt
```

### Adding dependencies
Adding development dependencies should go in `dev-requirements.in`.  Then,
execute:
```
pip-compile dev-requirements.in
```
to build the new `dev-requirements.txt`.

## Tests

To run the tests, execute:
```
python -m pytest -lvv tests/
```

or, if you have `tox` installed, execute:
```
tox
```
