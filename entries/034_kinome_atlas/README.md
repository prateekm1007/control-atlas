# Entry 034 — Human Kinome Atlas

Ingests the human kinome (~500 kinases) from AlphaFold DB.

## Usage

```bash
# Full kinome
python ingest_kinome.py --list kinase_list.txt

# Limited test run
python ingest_kinome.py --list kinase_list.txt --limit 10
