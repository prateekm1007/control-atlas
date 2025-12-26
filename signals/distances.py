import numpy as np
from scipy.spatial.distance import euclidean

def compute_distance_series(universe, residue_pairs, stride=10):
    ca = universe.select_atoms("name CA")
    resid_to_idx = {a.resid: i for i, a in enumerate(ca)}
    series = {p: [] for p in residue_pairs}

    for ts in universe.trajectory[::stride]:
        pos = ca.positions
        for i, j in residue_pairs:
            series[(i, j)].append(
                euclidean(pos[resid_to_idx[i]], pos[resid_to_idx[j]])
            )

    for k in series:
        arr = np.array(series[k])
        series[k] = arr - arr.mean()

    return series
