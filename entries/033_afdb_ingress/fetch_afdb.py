#!/usr/bin/env python3
""" Fetch structures from AlphaFold DB (2025 format). """
import requests
import gzip
import shutil
from pathlib import Path

AFDB_BASE = "https://alphafold.ebi.ac.uk/files"

def fetch_structure(uniprot_id: str, output_dir: Path) -> str | None:
    """ Download and decompress AFDB structure. Returns path or None. """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for version in ["v4", "v3", "v2", "v1"]:
        filename_gz = f"AF-{uniprot_id}-F1-model_{version}.pdb.gz"
        url = f"{AFDB_BASE}/{filename_gz}"
        gz_path = output_dir / filename_gz
        pdb_path = output_dir / f"AF-{uniprot_id}-F1-model_{version}.pdb"
        
        if pdb_path.exists():
            return str(pdb_path)
        
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                with open(gz_path, "wb") as f:
                    f.write(response.content)
                with gzip.open(gz_path, 'rb') as f_in:
                    with open(pdb_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                gz_path.unlink()  # cleanup gz
                return str(pdb_path)
        except Exception as e:
            print(f"[!] Error for {uniprot_id} v{version}: {e}")
            continue
    
    print(f"[!] Failed to download {uniprot_id}")
    return None
