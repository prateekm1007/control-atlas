from pathlib import Path
from backend_interface import generate_structure, BackendNotReady

def generate_structure(candidate, output_pdb: Path):
    raise BackendNotReady(
        "Chai backend declared but not yet connected"
    )
