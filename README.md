# aliquot-level-maf
Library to process aliquot-level MAF files.

This library requires Python 3.6+.

## Set up

This repository makes use of `pre-commit` for code formatting
and linting.  In order to make use of it, you must run the following
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
