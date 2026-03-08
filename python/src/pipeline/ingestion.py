"""Loads data_blocks and family_tree JSON files for all companies."""
import json
from pathlib import Path

import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Extend this list to add new companies
COMPANY_FOLDERS = ["companyA", "companyB", "companyC"]


def load_data_blocks(file_path: Path) -> pd.DataFrame | None:
    """Reads a data_blocks JSON file. Returns None if unreadable or missing duns."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error("Could not load %s: %s", file_path, e)
        return None

    if not data.get("duns"):
        logger.warning("%s: skipping data_blocks — no duns", file_path.parent.name)
        return None

    return pd.DataFrame([{
        "duns": data.get("duns"),
        "company_name": data.get("primaryName"),
        "start_date": data.get("startDate"),
        "country_iso": data.get("countryISOAlpha2Code"),
        "is_fortune_1000": data.get("isFortune1000Listed"),
        "website": next(iter(data.get("websiteAddress", [])), {}).get("url"),
    }])


def load_family_tree(file_path: Path) -> pd.DataFrame | None:
    """Reads a family_tree JSON file and returns hierarchy rows."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error("Could not load %s: %s", file_path, e)
        return None

    global_ultimate_id = data.get("globalUltimateDuns")
    records = []

    for m in data.get("familyTreeMembers", []):
        if not m.get("duns"):
            continue
        linkage = m.get("corporateLinkage") or {}
        records.append({
            "duns": m["duns"],
            "parent_company_id": (linkage.get("parent") or {}).get("duns"),
            "global_ultimate_id": global_ultimate_id,
            "hierarchy_level": linkage.get("hierarchyLevel"),
        })

    if not records:
        logger.warning("%s: no valid members in family tree", file_path.parent.name)
        return None

    return pd.DataFrame(records)


def ingest_all_companies(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Loads data_blocks and family_tree for all company folders."""
    db_frames, ft_frames = [], []

    for folder in COMPANY_FOLDERS:
        folder_path = data_dir / folder
        if not folder_path.exists():
            logger.warning("Folder not found, skipping: %s", folder)
            continue

        df = load_data_blocks(folder_path / "data_blocks_beautified.json")
        if df is not None:
            db_frames.append(df)

        df = load_family_tree(folder_path / "family_tree_beautified.json")
        if df is not None:
            ft_frames.append(df)

    if not db_frames:
        raise ValueError("No data_blocks loaded — check the data directory.")
    if not ft_frames:
        raise ValueError("No family_tree data loaded — check the data directory.")

    tree_count = sum(len(f) for f in ft_frames)
    logger.info("Loaded %d company record(s) and %d tree member(s)", len(db_frames), tree_count)
    return pd.concat(db_frames, ignore_index=True), pd.concat(ft_frames, ignore_index=True)
