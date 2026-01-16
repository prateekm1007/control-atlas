import numpy as np
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from scipy.spatial.distance import cdist

class SovereignJudge:
    def __init__(self, clash_threshold=1.2, clearance_min=2.5):
        self.clash_threshold = clash_threshold
        self.clearance_min = clearance_min

    def audit(self, path):
        """Tier-1 Geometric Veto. Checks for collisions and clearance."""
        try:
            d = MMCIF2Dict(path)
            coords = np.stack([np.array(d['_atom_site.Cartn_x'], dtype=float),
                              np.array(d['_atom_site.Cartn_y'], dtype=float),
                              np.array(d['_atom_site.Cartn_z'], dtype=float)], axis=1)
            
            chain_ids = np.array(d['_atom_site.label_asym_id'])
            u_chains = sorted(list(set(chain_ids)))
            
            # Length-aware identification
            counts = {c: np.sum(chain_ids == c) for c in u_chains}
            target_id = max(counts, key=counts.get)
            binder_id = min(counts, key=counts.get)
            
            tar_coords = coords[chain_ids == target_id]
            bin_coords = coords[chain_ids == binder_id]
            
            min_dist = np.min(cdist(tar_coords, bin_coords))
            
            # VETO LOGIC
            if min_dist < self.clash_threshold:
                return False, min_dist, "VETO: STERIC COLLISION"
            if min_dist < self.clearance_min:
                return False, min_dist, "VETO: INSUFFICIENT CLEARANCE"
                
            return True, min_dist, "PASS"
        except Exception as e:
            return False, 0.0, f"ERROR: {str(e)}"
