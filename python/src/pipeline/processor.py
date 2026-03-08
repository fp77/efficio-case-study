"""Enriches company records by joining with family tree hierarchy data."""
import pandas as pd

from src.utils.logger import get_logger
from src.utils.validators import validate_data_blocks, validate_family_tree

logger = get_logger(__name__)


def join_company_data(
    df_data_blocks: pd.DataFrame,
    df_family_tree: pd.DataFrame,
) -> pd.DataFrame:
    """Joins company records with family tree hierarchy data."""
    df_data_blocks = validate_data_blocks(df_data_blocks)
    df_family_tree = validate_family_tree(df_family_tree)

    enriched_df = pd.merge(
        df_data_blocks,
        df_family_tree[["duns", "parent_company_id", "hierarchy_level", "global_ultimate_id"]],
        on="duns",
        how="left",
    )

    # Sanity check: left join should never change row count
    if len(enriched_df) != len(df_data_blocks):
        logger.warning(
            "Row count changed after join: %d -> %d",
            len(df_data_blocks),
            len(enriched_df),
        )

    logger.info("Enrichment complete — %d row(s)", len(enriched_df))
    return enriched_df
