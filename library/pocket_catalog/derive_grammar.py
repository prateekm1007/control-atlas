#!/usr/bin/env python3
"""
Pan-Target Grammar Derivation
Analyzes 15 validated pockets to extract universal druggability rules
"""

import os
import json
import numpy as np

CATALOG = os.path.expanduser("~/control-atlas/library/pocket_catalog")
OUTPUT = os.path.expanduser("~/control-atlas/library/pocket_catalog/pan_target_grammar.json")

# Pocket class definitions
POCKET_CLASSES = {
    "SwitchII": ["KRAS_G12C", "KRAS_G12D", "HRAS_G12V", "NRAS_Q61R"],
    "KinaseHinge": ["BRAF_V600E", "EGFR_L858R", "ALK_F1174L", "RET_M918T"],
    "ActivationLoop": ["KIT_D816V", "PDGFRA_D842V"],
    "DNABinding": ["TP53_R175H", "TP53_R248Q"],
    "PHDomain": ["AKT1_E17K"],
    "Kinase": ["PIK3CA_H1047R"],
    "PhosphoSite": ["CTNNB1_S45F"]
}

def load_physics(target):
    path = os.path.join(CATALOG, target, "physics_metrics.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def derive_class_rules(targets):
    """Derive rules from a set of targets in the same class"""
    volumes = []
    exposures = []
    hydros = []
    
    for t in targets:
        m = load_physics(t)
        if m and m.get("status") == "computed":
            volumes.append(m["volume_A3"])
            exposures.append(m["exposure"])
            hydros.append(m["hydrophobic_pct"])
    
    if not volumes:
        return None
    
    return {
        "volume": {
            "mean": round(np.mean(volumes), 1),
            "std": round(np.std(volumes), 1),
            "range": [round(min(volumes), 1), round(max(volumes), 1)]
        },
        "exposure": {
            "mean": round(np.mean(exposures), 2),
            "std": round(np.std(exposures), 2),
            "range": [round(min(exposures), 2), round(max(exposures), 2)]
        },
        "hydrophobicity": {
            "mean": round(np.mean(hydros), 1),
            "std": round(np.std(hydros), 1),
            "range": [round(min(hydros), 1), round(max(hydros), 1)]
        },
        "n_targets": len(volumes)
    }

def derive_chemistry_rules(class_stats):
    """Convert physics stats to chemistry constraints"""
    rules = {}
    
    vol = class_stats["volume"]["mean"]
    exp = class_stats["exposure"]["mean"]
    hydro = class_stats["hydrophobicity"]["mean"]
    
    # Core scaffold size
    if vol > 2500:
        rules["core_size"] = "large"
        rules["max_rings"] = 5
        rules["mw_range"] = [450, 650]
    elif vol > 1500:
        rules["core_size"] = "medium"
        rules["max_rings"] = 4
        rules["mw_range"] = [350, 550]
    else:
        rules["core_size"] = "small"
        rules["max_rings"] = 3
        rules["mw_range"] = [250, 450]
    
    # Exposure -> Polarity requirements
    if exp > 30:
        rules["polar_tolerance"] = "high"
        rules["hba_range"] = [4, 10]
        rules["solubility_group"] = "required"
    elif exp > 20:
        rules["polar_tolerance"] = "medium"
        rules["hba_range"] = [3, 8]
        rules["solubility_group"] = "recommended"
    else:
        rules["polar_tolerance"] = "low"
        rules["hba_range"] = [2, 6]
        rules["solubility_group"] = "optional"
    
    # Hydrophobicity -> Anchor requirements
    if hydro > 40:
        rules["hydrophobic_anchor"] = "strong"
        rules["clogp_range"] = [3, 6]
    elif hydro > 25:
        rules["hydrophobic_anchor"] = "medium"
        rules["clogp_range"] = [2, 5]
    else:
        rules["hydrophobic_anchor"] = "weak"
        rules["clogp_range"] = [1, 4]
    
    return rules

def main():
    print("=== PAN-TARGET GRAMMAR DERIVATION ===")
    print("")
    
    grammar = {
        "version": "1.0",
        "description": "Universal druggability rules derived from 15 validated oncogenic pockets",
        "pocket_classes": {},
        "universal_rules": {},
        "class_specific_rules": {}
    }
    
    all_volumes = []
    all_exposures = []
    all_hydros = []
    
    print("POCKET CLASS ANALYSIS")
    print("-" * 60)
    
    for class_name, targets in POCKET_CLASSES.items():
        stats = derive_class_rules(targets)
        if stats:
            grammar["pocket_classes"][class_name] = {
                "targets": targets,
                "physics": stats
            }
            
            chem_rules = derive_chemistry_rules(stats)
            grammar["class_specific_rules"][class_name] = chem_rules
            
            print(f"{class_name} (n={stats['n_targets']})")
            print(f"  Volume: {stats['volume']['mean']} ± {stats['volume']['std']} A³")
            print(f"  Exposure: {stats['exposure']['mean']} ± {stats['exposure']['std']}")
            print(f"  Hydrophobic: {stats['hydrophobicity']['mean']} ± {stats['hydrophobicity']['std']}%")
            print(f"  -> Core: {chem_rules['core_size']}, Polar: {chem_rules['polar_tolerance']}, Anchor: {chem_rules['hydrophobic_anchor']}")
            print("")
            
            # Collect for universal stats
            for t in targets:
                m = load_physics(t)
                if m and m.get("status") == "computed":
                    all_volumes.append(m["volume_A3"])
                    all_exposures.append(m["exposure"])
                    all_hydros.append(m["hydrophobic_pct"])
    
    # Universal rules (across all classes)
    grammar["universal_rules"] = {
        "volume_range": [round(min(all_volumes), 1), round(max(all_volumes), 1)],
        "exposure_range": [round(min(all_exposures), 2), round(max(all_exposures), 2)],
        "hydrophobicity_range": [round(min(all_hydros), 1), round(max(all_hydros), 1)],
        "common_requirements": {
            "aromatic_core": True,
            "hbd_max": 4,
            "rotatable_bonds_max": 10,
            "warhead_optional": True,
            "warhead_types": ["acrylamide", "vinyl_sulfonamide", "chloroacetamide"]
        }
    }
    
    print("UNIVERSAL RULES (All Classes)")
    print("-" * 60)
    print(f"Volume Range: {grammar['universal_rules']['volume_range']} A³")
    print(f"Exposure Range: {grammar['universal_rules']['exposure_range']}")
    print(f"Hydrophobicity Range: {grammar['universal_rules']['hydrophobicity_range']}%")
    print("")
    
    # Save grammar
    with open(OUTPUT, "w") as f:
        json.dump(grammar, f, indent=2)
    
    print(f"Grammar saved to: {OUTPUT}")
    print("=== DERIVATION COMPLETE ===")

if __name__ == "__main__":
    main()
