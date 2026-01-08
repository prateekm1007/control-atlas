from pathlib import Path
from backend_interface import BackendNotReady

def generate_structure(candidate, output_pdb: Path):
    raise BackendNotReady(
        "RFdiffusion backend declared but not yet connected"
    )
