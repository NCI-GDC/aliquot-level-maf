from datetime import datetime

from aliquot_level_maf.selection import (
    PrimaryAliquotSelectionCriterion,
    select_primary_aliquots,
    SampleCriterion,
    PrimaryAliquot,
)


def test_select_primary_aliquots__selects_correct_sample_type():
    criteria = [
        PrimaryAliquotSelectionCriterion(
            id="1",
            samples=[
                SampleCriterion(id="sample_1", sample_type="Ectoplasm",),
                SampleCriterion(id="sample_2", sample_type="Muslin"),
            ],
            case_id="case_1",
            maf_creation_date=datetime(2020, 1, 1),
        ),
        PrimaryAliquotSelectionCriterion(
            id="2",
            samples=[
                SampleCriterion(id="sample_3", sample_type="Primary Tumor",),
                SampleCriterion(id="sample_4", sample_type="Blood Derived Normal",),
            ],
            case_id="case_1",
            maf_creation_date=datetime(2020, 1, 1),
        ),
        PrimaryAliquotSelectionCriterion(
            id="3",
            samples=[
                SampleCriterion(id="sample_5", sample_type="Unknown",),
                SampleCriterion(id="sample_6", sample_type="Recurrent Tumor",),
            ],
            case_id="case_1",
            maf_creation_date=datetime(2020, 1, 1),
        ),
    ]

    results = select_primary_aliquots(criteria)
    assert results["case_1"] == PrimaryAliquot(id="2", sample_id="sample_3")


def test_select_primary_aliquots__uses_maf_creation_date_to_break_tie():
    criteria = [
        PrimaryAliquotSelectionCriterion(
            id="1",
            samples=[
                SampleCriterion(id="sample_a", sample_type="Primary Tumor",),
                SampleCriterion(id="sample_b", sample_type="Blood Derived Normal"),
            ],
            case_id="case_1",
            maf_creation_date=datetime(2020, 1, 1),
        ),
        PrimaryAliquotSelectionCriterion(
            id="2",
            samples=[
                SampleCriterion(id="sample_d", sample_type="Primary Tumor",),
                SampleCriterion(id="sample_e", sample_type="Blood Derived Normal"),
            ],
            case_id="case_1",
            maf_creation_date=datetime(2020, 1, 2),
        ),
    ]

    results = select_primary_aliquots(criteria)
    assert results["case_1"] == PrimaryAliquot(id="1", sample_id="sample_a")


def test_select_primary_aliquots__handles_multiple_cases():
    criteria = [
        PrimaryAliquotSelectionCriterion(
            id="1",
            samples=[
                SampleCriterion(id="sample_1", sample_type="Ectoplasm",),
                SampleCriterion(id="sample_2", sample_type="Muslin"),
            ],
            case_id="case_1",
            maf_creation_date=datetime(2020, 1, 1),
        ),
        PrimaryAliquotSelectionCriterion(
            id="2",
            samples=[
                SampleCriterion(id="sample_3", sample_type="Primary Tumor",),
                SampleCriterion(id="sample_4", sample_type="Blood Derived Normal",),
            ],
            case_id="case_1",
            maf_creation_date=datetime(2020, 1, 1),
        ),
        PrimaryAliquotSelectionCriterion(
            id="3",
            samples=[
                SampleCriterion(id="sample_5", sample_type="Unknown",),
                SampleCriterion(id="sample_6", sample_type="Recurrent Tumor",),
            ],
            case_id="case_2",
            maf_creation_date=datetime(2020, 1, 1),
        ),
    ]

    results = select_primary_aliquots(criteria)
    assert results["case_1"] == PrimaryAliquot(id="2", sample_id="sample_3")
    assert results["case_2"] == PrimaryAliquot(id="3", sample_id="sample_6")


def test_select_primary_aliquots__no_criteria():
    results = select_primary_aliquots([])
    assert len(results.items()) == 0
