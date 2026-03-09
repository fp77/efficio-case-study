# Efficio Case Study

> **Note:** This project was developed with the assistance of Copilot. It was used to create the most of this README file, aid in the analysis of the input json files, assist in code debugging, and correcting pylint scoring. The codebase structure and overall design was entirely idealised by the developer.
---

## Overview

This repository contains my submission for the Efficio data engineering case study. The task involves working with company data sourced from the Dun & Bradstreet (D&B) API, covering three companies: **Microsoft**, **Harford Bank**, and **Bain Capital**.

The work is split into two parts:

- **Task 1 — Data Exploration:** Understanding the structure of the raw JSON files and thinking through how they could be modelled in a relational database. See [`data/companyA/README.md`](data/companyA/README.md) for the write-up.
- **Task 2 — Python Pipeline:** A small pipeline that ingests the JSON files, joins the company records with their corporate family tree data, and saves the result to Parquet.

---

## Repository Structure

```
efficio-case-study/
├── data/
│   ├── companyA/          # Microsoft — data_blocks + family_tree JSON
│   ├── companyB/          # Harford Bank
│   ├── companyC/          # Bain Capital
│   └── beautify_json.py   # Utility used to pretty-print the raw JSON files
├── python/
│   ├── src/
│   │   ├── main.py                   # Pipeline entry point
│   │   ├── pipeline/
│   │   │   ├── ingestion.py          # Loads JSON files into DataFrames
│   │   │   └── processor.py          # Joins data_blocks with family_tree
│   │   └── utils/
│   │       ├── logger.py             # Simple stdout logger
│   │       └── validators.py        # Input validation before the join
│   └── tests/
│       └── test_processor.py        # Unit test for join logic
├── output/                           # Parquet output (git-ignored)
├── requirements.txt
└── README.md
```

---

## Setup

**Prerequisites:** Python 3.10+

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Running the Pipeline

```bash
cd python/src
python main.py
```

The pipeline will:
1. Load `data_blocks_beautified.json` and `family_tree_beautified.json` for each company
2. Join the company records with their family tree hierarchy data
3. Save the enriched output to `output/enriched_companies.parquet`

---

## Running the Tests

```bash
cd python
PYTHONPATH=. python -m pytest tests/ -v
```

---

## Running the Linter

```bash
pylint python/src/ --max-line-length=100
```

---

## Pipeline Design

The pipeline follows a straightforward three-step structure:

**Ingest → Join → Save**

Each company folder contains two JSON files:
- `data_blocks_beautified.json` — top-level company information (name, country, website, etc.)
- `family_tree_beautified.json` — the full corporate hierarchy, with each member's DUNS, parent DUNS, and hierarchy level

The join uses the DUNS number as the key. The result is a left join, so every company from `data_blocks` appears in the output regardless of whether it has a match in the family tree.

Output columns: `duns`, `company_name`, `start_date`, `country_iso`, `is_fortune_1000`, `website`, `parent_company_id`, `hierarchy_level`, `global_ultimate_id`

---

## Scaling Considerations

The current implementation loads each JSON file fully into memory before processing. This works fine for the three companies in this exercise, but would become a bottleneck with hundreds of companies or very large JSON files. Two changes I would make to address this, without touching the underlying infrastructure:

**1. Stream large JSON files instead of loading them whole**

`json.load()` reads the entire file into memory at once. For large `family_tree` files (which can have thousands of members), this is wasteful. I would switch to [`ijson`](https://pypi.org/project/ijson/), a streaming JSON parser that iterates over the `familyTreeMembers` array incrementally. This keeps memory usage flat regardless of file size:

```python
import ijson

with open(file_path, "rb") as f:
    for member in ijson.items(f, "familyTreeMembers.item"):
        # process one member at a time
```

**2. Process companies in parallel**

Right now `ingest_all_companies` loops over company folders sequentially. With many companies, the I/O time adds up. I would replace the `for` loop with `concurrent.futures.ThreadPoolExecutor` to load and parse multiple company folders at the same time — no infrastructure changes needed, just standard library:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor() as executor:
    results = list(executor.map(load_company, company_folders))
```

Together these two changes would let the pipeline handle a much larger number of companies with larger files while staying within the same memory and compute footprint.
