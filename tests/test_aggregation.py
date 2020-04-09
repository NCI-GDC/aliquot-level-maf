import contextlib
import gzip
import tempfile
from typing import BinaryIO, List
import io

import freezegun
import pytest

from aliquot_level_maf.aggregation import (
    aggregate_mafs,
    AliquotLevelMaf,
    ValidationError,
)


def _aggregate_multiple_mafs(filenames: List[str], output: BinaryIO) -> None:
    with contextlib.ExitStack() as stack:
        files = [stack.enter_context(open(filename, "rb")) for filename in filenames]
        mafs = [
            AliquotLevelMaf(
                file=files[i], tumor_aliquot_submitter_id=f"submitter_id_{i}"
            )
            for i in range(len(files))
        ]
        aggregate_mafs(mafs, output)


def test_aggregate_mafs__check_line_count():
    with tempfile.TemporaryFile(mode="w+b") as file:
        _aggregate_multiple_mafs(
            filenames=[
                "tests/resources/example_0.wxs.aliquot_ensemble_masked.maf.gz",
                "tests/resources/example_1.wxs.aliquot_ensemble_masked.maf.gz",
            ],
            output=file,
        )
        file.seek(0)
        with io.BufferedReader(gzip.open(file, "r")) as reader:
            lines = [line.decode() for line in reader.readlines()]
            pragmas = [line for line in lines if line.startswith("#")]
            headers = [line for line in lines if line.startswith("Hugo_Symbol")]
            assert len(lines) == 17
            assert len(pragmas) == 5
            assert len(headers) == 1


@freezegun.freeze_time("2020-03-23")
def test_aggregate_mafs__correct_file_header():
    """Project-level MAF files should start with 5 pragmas."""
    with tempfile.TemporaryFile(mode="w+b") as file:
        _aggregate_multiple_mafs(
            filenames=[
                "tests/resources/example_0.wxs.aliquot_ensemble_masked.maf.gz",
                "tests/resources/example_1.wxs.aliquot_ensemble_masked.maf.gz",
            ],
            output=file,
        )
        file.seek(0)
        with io.BufferedReader(gzip.open(file, "r")) as reader:
            assert reader.readline().decode() == "#version gdc-1.0.0\n"
            assert reader.readline().decode() == "#filedate 20200323\n"
            assert (
                reader.readline().decode()
                == "#annotation.spec gdc-1.0.0-aliquot-merged-masked\n"
            )
            assert reader.readline().decode() == "#n.analyzed.samples 2\n"
            assert (
                reader.readline().decode()
                == "#tumor.aliquots.submitter_id submitter_id_0,submitter_id_1\n"
            )


def test_aggregate_mafs__no_mafs():
    """If not mafs are given, then no output should be written."""
    output = tempfile.TemporaryFile()
    aggregate_mafs([], output)
    assert output.tell() == 0


def test_aggregate_mafs__different_versions_fail():
    with pytest.raises(ValidationError, match="same version"):
        with tempfile.TemporaryFile(mode="w+b") as file:
            _aggregate_multiple_mafs(
                filenames=[
                    "tests/resources/example_0.wxs.aliquot_ensemble_masked.maf.gz",
                    "tests/resources/different_version.maf.gz",
                ],
                output=file,
            )


def test_aggregate_mafs__different_annotation_specs_fail():
    with pytest.raises(ValidationError, match="same annotation spec"):
        with tempfile.TemporaryFile(mode="w+b") as file:
            _aggregate_multiple_mafs(
                filenames=[
                    "tests/resources/example_0.wxs.aliquot_ensemble_masked.maf.gz",
                    "tests/resources/different_annotation_spec.maf.gz",
                ],
                output=file,
            )


def test_aggregate_mafs__different_headers_fail():
    with pytest.raises(ValidationError, match="same column headers"):
        with tempfile.TemporaryFile(mode="w+b") as file:
            _aggregate_multiple_mafs(
                filenames=[
                    "tests/resources/example_0.wxs.aliquot_ensemble_masked.maf.gz",
                    "tests/resources/different_headers.maf.gz",
                ],
                output=file,
            )
