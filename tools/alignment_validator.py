import numpy as np
from Bio.PDB import PDBParser, MMCIFParser, Superimposer
import os

class SovereignValidator:
    def __init__(self, ref_pdb="ref_5NIU.pdb"):
        self.ref_pdb = ref_pdb
        self.parser_pdb = PDBParser(QUIET=True)
        self.parser_cif = MMCIFParser(QUIET=True)

    def _get_structure(self, path):
        if path.endswith('.cif'):
            return self.parser_cif.get_structure("fixed", path)[0]
        return self.parser_pdb.get_structure("moving", path)[0]

    def _collect_warhead_atoms(self, chain):
        """Surgical extraction of functional motif heavy atoms."""
        warhead_res = ['TYR', 'TRP', 'PRO', 'THR', 'GLY']
        atoms = []
        for res in chain:
            if res.get_resname() in warhead_res:
                for atom in res:
                    if atom.element != 'H':
                        atoms.append(atom)
        return atoms

    def _collect_backbone_ca(self, chain):
        """Extraction of target backbone for Stage 1 alignment."""
        return [res["CA"] for res in chain if "CA" in res]

    def validate_lead(self, moving_path):
        """
        Industrial Two-Stage Audit:
        STAGE 1: Superimpose Target Backbones (Coordinate Lock).
        STAGE 2: Measure Warhead RMSD without further superposition.
        """
        ref_struct = self._get_structure(self.ref_pdb)
        mov_struct = self._get_structure(moving_path)

        # IDENTIFY CHAINS (Length-Aware)
        ref_target = sorted(list(ref_struct.get_chains()), key=lambda c: len(list(c.get_atoms())), reverse=True)[0]
        ref_binder = sorted(list(ref_struct.get_chains()), key=lambda c: len(list(c.get_atoms())), reverse=True)[1]
        
        mov_target = sorted(list(mov_struct.get_chains()), key=lambda c: len(list(c.get_atoms())), reverse=True)[0]
        mov_binder = sorted(list(mov_struct.get_chains()), key=lambda c: len(list(c.get_atoms())), reverse=True)[1]

        # --- STAGE 1: BACKBONE SUPERPOSITION ---
        ref_ca = self._collect_backbone_ca(ref_target)
        mov_ca = self._collect_backbone_ca(mov_target)
        
        # Ensure identical atom counts for alignment
        min_len = min(len(ref_ca), len(mov_ca))
        sup = Superimposer()
        sup.set_atoms(ref_ca[:min_len], mov_ca[:min_len])
        sup.apply(mov_struct.get_atoms())
        print(f"✅ STAGE 1: Target backbones aligned (RMSD: {sup.rms:.4f} Å)")

        # --- STAGE 2: WARHEAD GEOMETRY AUDIT ---
        ref_wh = self._collect_warhead_atoms(ref_binder)
        mov_wh = self._collect_warhead_atoms(mov_binder)
        
        # Calculate RMSD of the warhead in the NOW-LOCKED coordinate frame
        diff = np.array([a.coord for a in mov_wh]) - np.array([a.coord for a in ref_wh])
        motif_rmsd = np.sqrt(np.mean(np.sum(diff**2, axis=1)))

        print(f"🏆 STAGE 2: Warhead Local RMSD (YWPTG): {motif_rmsd:.4f} Å")
        return motif_rmsd

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        v = SovereignValidator()
        v.validate_lead(sys.argv[1])
