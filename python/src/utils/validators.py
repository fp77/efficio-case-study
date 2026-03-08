"""Validation helpers used by processor.py."""
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def validate_data_blocks(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with no duns — they can't be identified."""
    before = len(df)
    df = df.dropna(subset=["duns"]).drop_duplicates(subset=["duns"])
    if len(df) < before:
        logger.warning("data_blocks: removed %d row(s) with null/duplicate duns", before - len(df))
    return df


def validate_family_tree(df: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate family tree by duns."""
    before = len(df)
    df = df.dropna(subset=["duns"]).drop_duplicates(subset=["duns"])
    if len(df) < before:
        logger.warning("family_tree: removed %d row(s) with null/duplicate duns", before - len(df))
    return df
