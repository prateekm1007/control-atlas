import numpy as np
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from scipy.spatial.distance import cdist

def calculate_clearance(cif_path):
    """Sovereign length-aware chain identification and clearance audit."""
    d = MMCIF2Dict(cif_path)
    coords = np.stack([np.array(d['_atom_site.Cartn_x'], dtype=float),
                      np.array(d['_atom_site.Cartn_y'], dtype=float),
                      np.array(d['_atom_site.Cartn_z'], dtype=float)], axis=1)
    
    chain_ids = np.array(d['_atom_site.label_asym_id'])
    u_chains = sorted(list(set(chain_ids)))
    
    # Identify Target (Largest) vs Binder (Smallest)
    counts = {c: np.sum(chain_ids == c) for c in u_chains}
    target_id = max(counts, key=counts.get)
    binder_id = min(counts, key=counts.get)
    
    t_coords = coords[chain_ids == target_id]
    b_coords = coords[chain_ids == binder_id]
    
    return round(float(np.min(cdist(t_coords, b_coords))), 2)
