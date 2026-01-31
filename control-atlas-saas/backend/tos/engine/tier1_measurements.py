import numpy as np
from typing import Tuple, Dict
from .chemistry_registry import is_contextually_bonded

class Tier1Measurements:
    @staticmethod
    def check_law_155_L(structure, threshold: float = 2.0) -> Tuple[str, str, Dict]:
        """
        LAW-155-L: Voxel-Accelerated Steric Clash (Exact O(N)).
        Prunes pairs using a 3.0A spatial grid. Bit-for-bit parity with naive.
        """
        all_atoms = structure.atoms + structure.ligands
        if not all_atoms: return "PASS", "No atoms.", {}
        
        # 1. Build Spatial Grid
        grid = {}
        voxel_size = 3.0
        coords = np.array([a.pos for a in all_atoms])
        
        for idx, a in enumerate(all_atoms):
            v_coord = tuple((coords[idx] // voxel_size).astype(int))
            if v_coord not in grid: grid[v_coord] = []
            grid[v_coord].append(idx)
            
        # 2. Exact Search (Current + 26 Neighbors)
        for v_coord, atom_indices in grid.items():
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        neighbor_v = (v_coord[0]+dx, v_coord[1]+dy, v_coord[2]+dz)
                        if neighbor_v not in grid: continue
                        
                        for i in atom_indices:
                            for j in grid[neighbor_v]:
                                if i >= j: continue # Unique pairs only
                                
                                a1, a2 = all_atoms[i], all_atoms[j]
                                d = np.linalg.norm(coords[i] - coords[j])
                                
                                # Covalent/Contextual Pruning (Step 5.13 Logic Frozen)
                                if a1.chain == a2.chain and abs(a1.res_seq - a2.res_seq) <= 1 and d < 1.65: continue
                                if is_contextually_bonded(a1, a2, d): continue
                                if a1.chain == a2.chain and a1.res_seq == a2.res_seq: continue

                                # Steric Veto
                                if d < threshold:
                                    anchor = {"chain": a1.chain, "res_seq": a1.res_seq, "pos": a1.pos}
                                    return "FAIL", f"Clash: {a1.chain}:{a1.res_name}{a1.res_seq} @ {d:.2f}A", anchor
                                    
        return "PASS", f"Verified {len(all_atoms)} atoms via Spatial Grid.", {}

    @staticmethod
    def check_law_160(structure, threshold: float = 4.5) -> Tuple[str, str, Dict]:
        cas = [a for a in structure.atoms if a.atom_name == "CA"]
        for i in range(len(cas) - 1):
            c1, c2 = cas[i], cas[i+1]
            if c1.chain == c2.chain:
                d = np.linalg.norm(np.array(c1.pos) - np.array(c2.pos))
                if d > threshold:
                    return "FAIL", f"Torn chain {c1.res_seq}-{c2.res_seq} @ {d:.2f}A", {"chain": c1.chain, "res_seq": c1.res_seq, "pos": c1.pos}
        return "PASS", "Backbone continuity verified.", {}
