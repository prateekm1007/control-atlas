from MDAnalysis.analysis.rms import RMSF

def compute_rmsf(universe):
    ca = universe.select_atoms("name CA")
    rmsf = RMSF(ca).run()
    return dict(zip(ca.resids, rmsf.rmsf))
