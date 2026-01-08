from pathlib import Path
import subprocess

def run_inference(
    buffer: str,
    anchor: str,
    scaffold: str,
    hinge: str,
    output_pdb: Path
):
    """
    Canonical Chai-1 inference adapter.
    Calls run_pd_l1_v15.py and writes a real PDB to output_pdb.
    """

    output_pdb = Path(output_pdb)
    output_pdb.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "python3",
        "run_pd_l1_v15.py",
        "--buffer", buffer,
        "--anchor", anchor,
        "--scaffold", scaffold,
        "--hinge", hinge,
        "--out", str(output_pdb)
    ]

    print("🧬 Chai-1 inference command:")
    print(" ", " ".join(cmd))

    subprocess.run(cmd, check=True)
