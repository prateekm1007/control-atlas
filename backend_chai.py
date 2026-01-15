import os
import torch
from chai_lab.chai1 import run_inference
from pathlib import Path

class ChaiBackend:
    def __init__(self, output_root="/kaggle/working/outputs"):
        self.output_root = Path(output_root)
        self.output_root.mkdir(parents=True, exist_ok=True)

    def run_constrained_docking(self, fasta_path, constraint_path=None, seed=42):
        """Executes industrial-grade inference with optional Zn2+ constraints."""
        run_inference(
            fasta_file=Path(fasta_path),
            output_dir=self.output_root,
            constraint_path=Path(constraint_path) if constraint_path else None,
            num_trunk_recycles=3,
            num_diffn_timesteps=200,
            seed=seed,
            device=torch.device("cuda:0")
        )
        return list(self.output_root.glob("*.cif"))
