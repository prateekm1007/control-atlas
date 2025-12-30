#!/usr/bin/env python3
"""
Fetch structures from AlphaFold DB.
"""

import requests
import sys
from pathlib import Path
from time import sleep

AFDB_API_URL = "https://alphafold.ebi.ac.uk/files"

def fetch_structure(uniprot_id: str, output_dir: Path) -> str:
    """
    Download the predicted structure (PDB) for a UniProt ID.
    Returns path to file or None.
    """
    # Try v4 first
    filename = f"AF-{uniprot_id}-F1-model_v4.pdb"
    url = f"{AFDB_API_URL}/{filename}"
    output_path = output_dir / filename
    
    if output_path.exists():
        return str(output_path)
    
    try:
        sleep(0.5) # Be polite to API
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return str(output_path)
        else:
            # Try v3
            filename_v3 = f"AF-{uniprot_id}-F1-model_v3.pdb"
            url_v3 = f"{AFDB_API_URL}/{filename_v3}"
            response = requests.get(url_v3, timeout=30)
            if response.status_code == 200:
                output_path = output_dir / filename_v3
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return str(output_path)
            
            print(f"[!] Failed to download {uniprot_id}: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"[!] Error fetching {uniprot_id}: {e}")
        return None
