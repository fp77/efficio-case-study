"""Pipeline entry point: ingest, enrich, and save company data to Parquet."""
import sys
from pathlib import Path

# Allow running as `python src/main.py` from the python/ directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# pylint: disable=wrong-import-position
from src.pipeline.ingestion import ingest_all_companies
from src.pipeline.processor import join_company_data
from src.utils.logger import get_logger

BASE_DIR = Path(__file__).resolve().parent.parent.parent
logger = get_logger(__name__)


def main() -> None:
    """Run the full ingestion and enrichment pipeline."""
    data_dir = BASE_DIR / "data"
    output_dir = BASE_DIR / "output"
    output_dir.mkdir(exist_ok=True)

    try:
        # 1. Ingest
        df_data_blocks, df_family_tree = ingest_all_companies(data_dir)

        # 2. Enrich
        enriched_df = join_company_data(df_data_blocks, df_family_tree)
        logger.info("\n%s", enriched_df.to_string(index=False))

        # 3. Save
        output_path = output_dir / "enriched_companies.parquet"
        enriched_df.to_parquet(output_path, index=False, engine="pyarrow")
        logger.info("Saved to %s", output_path)

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Pipeline failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
