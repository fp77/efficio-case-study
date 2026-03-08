"""Unit tests for the join_company_data function."""
import pandas as pd

from src.pipeline.processor import join_company_data


def test_join_attaches_hierarchy_fields():
    """
    Verify join_company_data correctly attaches hierarchy fields from the family tree.
    """
    data_blocks = pd.DataFrame([
        {"duns": "111111111", "company_name": "A"},
        {"duns": "222222222", "company_name": "B"},
        {"duns": "999999999", "company_name": "C"},  # not in family tree
    ])

    family_tree = pd.DataFrame([
        {
            "duns": "111111111",
            "parent_company_id": None,
            "hierarchy_level": 1,
            "global_ultimate_id": "111111111",
        },
        {
            "duns": "222222222",
            "parent_company_id": "111111111",
            "hierarchy_level": 2,
            "global_ultimate_id": "111111111",
        },
    ])

    result = join_company_data(data_blocks, family_tree)

    # All input rows are preserved
    assert len(result) == 3

    # Hierarchy fields are correctly attached
    a = result[result["duns"] == "111111111"].iloc[0]
    assert a["hierarchy_level"] == 1
    assert pd.isna(a["parent_company_id"])

    b = result[result["duns"] == "222222222"].iloc[0]
    assert b["hierarchy_level"] == 2
    assert b["parent_company_id"] == "111111111"

    # Company missing from the family tree gets NaN — not dropped
    c = result[result["duns"] == "999999999"].iloc[0]
    assert pd.isna(c["hierarchy_level"])

