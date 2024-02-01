import datetime
import gzip
import io
from collections import OrderedDict
from typing import NamedTuple, BinaryIO, List, Dict, TextIO, Optional


class ValidationError(Exception):
    """Error when validating a MAF file.

    Attributes:
        message: A short message describing the validation error
        details: A longer message containing details of the validation error
    """

    def __init__(self, message, details):
        self.message = message
        self.details = details

    def __str__(self):
        return f"{self.message}\n{self.details}"


class AliquotLevelMaf(NamedTuple):
    """The name and content of an aliquot-level MAF file.

    The file is assumed to be gzipped.

    Attributes:
        file: A file-like object representing the content of aliquot-level MAF file.
        tumor_aliquot_submitter_id: The submitter id of the tumor aliquot.
    """

    file: BinaryIO
    tumor_aliquot_submitter_id: str


def aggregate_mafs(mafs: List[AliquotLevelMaf], output: BinaryIO) -> None:
    """Aggregate a given list of aliquot-level MAF files.

    The aliquot-level MAF files will be combined into a single MAF file and written to
    the given output file-like object.

    The input files are assumed to be gzipped MAF files.  The output will be written
    as a gzipped MAF file.

    Args:
        mafs: A list of aliquot-level MAF files with metadata.
        output: A file-like object to write the aggregated MAF file.
    """
    if not mafs:
        return

    with gzip.open(output, "wt") as gzip_output:
        is_first_pass = True
        for maf in mafs:
            with io.BufferedReader(gzip.open(maf.file, "r")) as reader:
                # Case where the file content is empty or the user does not have access
                # to a file.
                file_headers = _read_and_parse_file_headers(reader)
                if not file_headers:
                    continue
                if is_first_pass:
                    expected_file_headers = file_headers
                _validate_file_headers(
                    headers=file_headers, expected_headers=expected_file_headers
                )

                column_headers = _read_and_parse_column_headers(reader)
                if is_first_pass:
                    expected_column_headers = column_headers.copy()
                _validate_column_headers(
                    headers=column_headers, expected_headers=expected_column_headers
                )

                if is_first_pass:
                    _write_file_headers(
                        output=gzip_output,
                        version=file_headers.version,
                        file_date=datetime.datetime.now(),
                        annotation_spec=file_headers.annotation_spec,
                        submitter_ids=[m.tumor_aliquot_submitter_id for m in mafs],
                    )
                    _write_column_headers(gzip_output, column_headers)

                for line in reader:
                    gzip_output.write(line.decode())

            is_first_pass = False


class _MafFileHeader(NamedTuple):
    version: str
    annotation_spec: str
    properties: Dict[str, str]


class _MafFileHeaderBuilder:
    def __init__(self):
        self.version = None
        self.annotation_spec = None
        self.properties = OrderedDict()

    def set_version(self, version: str) -> "_MafFileHeaderBuilder":
        self.version = version
        return self

    def set_annotation_spec(self, annotation_spec: str) -> "_MafFileHeaderBuilder":
        self.annotation_spec = annotation_spec
        return self

    def add_property(self, key: str, value: str) -> "_MafFileHeaderBuilder":
        self.properties[key] = value
        return self

    def build(self) -> Optional[_MafFileHeader]:
        # If there are no properties then the response from the query was empty.
        if not self.properties:
            return None

        if not self.version:
            raise ValueError("version must be defined")

        if not self.annotation_spec:
            raise ValueError("annotation spec must be defined")

        return _MafFileHeader(
            version=self.version,
            annotation_spec=self.annotation_spec,
            properties=self.properties,
        )


def _read_and_parse_file_headers(reader: io.BufferedReader) -> Optional[_MafFileHeader]:
    builder = _MafFileHeaderBuilder()
    while reader.peek(1) and reader.peek(1).decode()[0] == "#":
        line = reader.readline().decode().rstrip()[1:]
        key, value = line.split(" ", 1)
        if key == "version":
            builder.set_version(value)
        elif key == "annotation.spec":
            builder.set_annotation_spec(value)
        else:
            builder.add_property(key, value)
    return builder.build()


def _validate_file_headers(
    headers: _MafFileHeader, expected_headers: _MafFileHeader
) -> None:
    errors = list()
    if not headers.version == expected_headers.version:
        errors.append(
            f"All files must have the same version.  File version {headers.version} \
            does not match version {expected_headers.version}"
        )

    if not headers.annotation_spec == expected_headers.annotation_spec:
        errors.append(
            f"All files must have the same annotation spec.  File annotation spec \
            {headers.annotation_spec} does not match version \
            {expected_headers.annotation_spec}"
        )

    if errors:
        raise ValidationError(
            message="Failed file header validation.", details="\n".join(errors)
        )


def _read_and_parse_column_headers(reader: io.BufferedReader) -> List[str]:
    line = reader.readline().decode().rstrip()
    return line.split("\t")


def _validate_column_headers(headers: List[str], expected_headers: List[str]) -> None:
    if not headers == expected_headers:
        raise ValidationError(
            message="All files must have the same column headers.",
            details=f"Got: {headers}\nExpected: {expected_headers}",
        )


def _write_file_headers(
    output: TextIO,
    version: str,
    file_date: datetime.datetime,
    annotation_spec: str,
    submitter_ids: List[str],
) -> None:
    header_lines = [
        f"#version {version}\n",
        f"#filedate {file_date.strftime('%Y%m%d')}\n",
        f"#annotation.spec {annotation_spec}\n",
        f"#n.analyzed.samples {len(submitter_ids)}\n",
        f"#tumor.aliquots.submitter_id {','.join(submitter_ids)}\n",
    ]
    output.writelines(header_lines)


def _write_column_headers(output: TextIO, column_headers: List[str]) -> None:
    output.write("\t".join(column_headers))
    output.write("\n")
