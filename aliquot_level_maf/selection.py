import datetime
import sys
from collections import defaultdict
from typing import Dict, List, NamedTuple

# This is the order that sample types should be selected.
# Lowest rank wins.
_SAMPLE_TYPE_RANK: Dict[str, int] = {
    "Primary Tumor": 1,
    "Primary Blood Derived Cancer - Bone Marrow": 2,
    "Primary Blood Derived Cancer - Peripheral Blood": 3,
    "Metastatic": 4,
    "Additional Metastatic": 5,
    "Recurrent Tumor": 6,
    "Recurrent Blood Derived Cancer - Bone Marrow": 7,
    "Recurrent Blood Derived Cancer - Peripheral Blood": 8,
    "Additional - New Primary": 9,
}

# Any sample type that is not explicitly ranked should get a default rank that puts
# it at the bottom of the ranking.
_MAX_SORT_RANK = sys.maxsize


class SampleCriterion(NamedTuple):
    """Attributes describing a sample for primary-aliquot selection.

    Attributes:
        id: The id of the sample.
        sample_type: The type of the sample.
    """

    id: str
    sample_type: str


class PrimaryAliquotSelectionCriterion(NamedTuple):
    """Attributes of an aliquot-level MAF file used to perform primary-aliquot selection.

    Attributes:
        id: Any identifier.
        samples: The samples that the aliquots came from.
        case_id: The id of the case that the aliquot came from.
        maf_creation_date: The date the MAF file was created in the graph.
    """

    id: str
    samples: List[SampleCriterion]
    case_id: str
    maf_creation_date: datetime.datetime


class PrimaryAliquot(NamedTuple):
    """The result of primary-aliquot selection.

    Attributes:
        id: The primary identifier given in PrimaryAliquotSelectionCriterion
        sample_id: The id of the sample selected.  This id comes from SampleCriterion.id
    """

    id: str
    sample_id: str


def select_primary_aliquots(
    criteria: List[PrimaryAliquotSelectionCriterion],
) -> Dict[str, PrimaryAliquot]:
    """Select the primary-aliquot for each case.

    For primary aliquot selection, the MAFs are ranked based on sample.sample_type, in
    the following order:

    Primary Tumor
    Primary Blood Derived Cancer - Bone Marrow
    Primary Blood Derived Cancer - Peripheral Blood
    Metastatic
    Additional Metastatic
    Recurrent Tumor
    Recurrent Blood Derived Cancer - Bone Marrow
    Recurrent Blood Derived Cancer - Peripheral Blood
    Additional - New Primary
    Any other sample types

    If there are still ties, we will pick the MAF with the earliest creation date in
    GDC Graph.

    Args:
        criteria: A list of selection criteria for each aliquot-level MAF

    Returns:
        A dictionary of case ids to primary aliquot
    """
    if not criteria:
        return dict()

    criteria_by_case = _group_criteria_by_case(_flatten(criteria))
    return {case_id: _perform_selection(cs) for case_id, cs in criteria_by_case.items()}


def _flatten(
    criteria: List[PrimaryAliquotSelectionCriterion],
) -> List[PrimaryAliquotSelectionCriterion]:
    """Flatten selection criteria to have one sample per criterion."""
    flattened = list()
    for criterion in criteria:
        for sample in criterion.samples:
            flattened.append(
                PrimaryAliquotSelectionCriterion(
                    id=criterion.id,
                    samples=[sample],
                    case_id=criterion.case_id,
                    maf_creation_date=criterion.maf_creation_date,
                )
            )
    return flattened


def _group_criteria_by_case(
    criteria: List[PrimaryAliquotSelectionCriterion],
) -> Dict[str, List[PrimaryAliquotSelectionCriterion]]:
    criteria_by_case = defaultdict(list)
    for criterion in criteria:
        criteria_by_case[criterion.case_id].append(criterion)
    return criteria_by_case


def _perform_selection(
    criteria: List[PrimaryAliquotSelectionCriterion],
) -> PrimaryAliquot:
    primary = _tiebreaker(_select_by_sample_type(criteria))
    return PrimaryAliquot(id=primary.id, sample_id=primary.samples[0].id)


def _get_sort_rank(criterion: PrimaryAliquotSelectionCriterion) -> int:
    """Calculate rank for a given criterion.

    An aliquot-level MAF file can be associated with multiple samples.  This
    is usually a tumor sample and a normal sample.  This function will
    calculate the selection rank for each sample and return the best one
    for primary-aliquot selection.

    Args:
        criterion: The criterion for a MAF file.

    Returns:
        An integer rank where lowest wins
    """
    ranks = [
        _SAMPLE_TYPE_RANK.get(sample.sample_type, _MAX_SORT_RANK)
        for sample in criterion.samples
    ]
    return min(ranks)


def _select_by_sample_type(
    criteria: List[PrimaryAliquotSelectionCriterion],
) -> List[PrimaryAliquotSelectionCriterion]:
    current_rank = _MAX_SORT_RANK
    primaries = []
    for criterion in criteria:
        rank = _get_sort_rank(criterion)

        if not primaries or rank < current_rank:
            primaries = [criterion]
            current_rank = rank
            continue

        if rank == current_rank:
            primaries.append(criterion)
            continue

    return primaries


def _tiebreaker(
    criteria: List[PrimaryAliquotSelectionCriterion],
) -> PrimaryAliquotSelectionCriterion:
    """Choose the tiebreaker in the event that the ranks are the same

    First sort on the created datetime for the maf.
    Then sort by the string representation of the uuid for the maf.
    """

    return sorted(criteria, key=lambda c: (c.maf_creation_date, c.id))[0]
