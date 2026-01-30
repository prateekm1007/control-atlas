import numpy as np
from typing import Tuple, Dict
from .chemistry_registry import is_contextually_bonded

class Tier1Measurements:
    @staticmethod
    def check_law_155_L(structure, threshold: float = 2.0) -> Tuple[str, str, Dict]:
        """
        LAW-155-L: Context-Aware Steric Exclusion.
        Now enforces residue identity for disulfides and metal coordination.
        """
        all_atoms = structure.atoms + structure.ligands
        num_atoms = len(all_atoms)
        coords = np.array([a.pos for a in all_atoms])
        
        for i in range(num_atoms):
            for j in range(i + 1, num_atoms):
                a1, a2 = all_atoms[i], all_atoms[j]
                dist = np.linalg.norm(coords[i] - coords[j])
                
                # 1. PEPTIDE BOND OVERRIDE (C-N Adjacency)
                if a1.chain == a2.chain and abs(a1.res_seq - a2.res_seq) == 1:
                    if (a1.atom_name == "C" and a2.atom_name == "N") or \
                       (a1.atom_name == "N" and a2.atom_name == "C"):
                        if dist < 1.65: continue

                # 2. CONTEXT-AWARE CHEMISTRY (The Fix)
                if is_contextually_bonded(a1, a2, dist):
                    continue
                
                # 3. INTRA-RESIDUE EXCLUSION (Documented technical debt)
                if a1.chain == a2.chain and a1.res_seq == a2.res_seq:
                    continue

                # 4. STERIC CLASH VETO
                if dist < threshold:
                    anchor = {"chain": a1.chain, "res_seq": a1.res_seq, "pos": a1.pos}
                    return "FAIL", f"Clash: {a1.chain}:{a1.res_name}{a1.res_seq}({a1.atom_name}) @ {dist:.2f}A", anchor
        
        return "PASS", f"Verified {num_atoms} atoms against Contextual Canon.", {}

    @staticmethod
    def check_law_160(structure, threshold: float = 4.5) -> Tuple[str, str, Dict]:
        cas = [a for a in structure.atoms if a.atom_name == "CA"]
        for i in range(len(cas) - 1):
            c1, c2 = cas[i], cas[i+1]
            if c1.chain == c2.chain:
                dist = np.linalg.norm(np.array(c1.pos) - np.array(c2.pos))
                if dist > threshold:
                    return "FAIL", f"Torn chain {c1.res_seq}-{c2.res_seq} @ {dist:.2f}A", {"chain": c1.chain, "res_seq": c1.res_seq, "pos": c1.pos}
        return "PASS", "Backbone continuity verified.", {}
