[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

---

# aliquot-level-maf
Library to process aliquot-level MAF files.

This library requires Python 3.6+.

- [aliquot-level-maf](#aliquot-level-maf)
  - [Install `pre-commit`](#install-pre-commit)
    - [Update secrets baseline for `detect-secrets`](#update-secrets-baseline-for-detect-secrets)
  - [Dependencies](#dependencies)
    - [Installing dependencies](#installing-dependencies)
    - [Adding dependencies](#adding-dependencies)
  - [Tests](#tests)

## Install `pre-commit`

This repository makes use of `pre-commit` for code formatting, linting
and secrets detecting.  In order to make use of it, you must run the following
commands to install `pre-commit`.
```
pip install -r dev-requirements.txt
pre-commit install
```

### Update secrets baseline for `detect-secrets`

We use [detect-secrets](https://github.com/Yelp/detect-secrets) to search for secrets being committed into the repo.

To update the .secrets.baseline file run
```
detect-secrets scan --update .secrets.baseline
```

`.secrets.baseline` contains all the string that were caught by detect-secrets but are not stored in plain text. Audit the baseline to view the secrets .

```
detect-secrets audit .secrets.baseline
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
