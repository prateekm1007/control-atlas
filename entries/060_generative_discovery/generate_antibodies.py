#!/usr/bin/env python3
import json
import random
import argparse

ANCHOR_SUFFIX = "FDY"
FORBIDDEN = ["NG", "NS", "DG"]

WEIGHTED_POOL = (
    "Y"*6 +
    "W"*2 + "F"*2 +
    "S"*4 + "G"*4 +
    "V"*2 + "I"*2 + "T"*2 +
    "ADEHKLNPQR"
)

def generate_structured_cdr3(target_len=12):
    core_len = target_len - len(ANCHOR_SUFFIX)
    while True:
        core = "".join(random.choice(WEIGHTED_POOL) for _ in range(core_len))
        cdr3 = core + ANCHOR_SUFFIX
        if any(m in cdr3 for m in FORBIDDEN):
            continue
        if "C" in cdr3:
            continue
        return cdr3

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num", type=int, default=5)
    parser.add_argument("--out", type=str, default="candidates.json")
    args = parser.parse_args()

    vh_prefix = "EVQLVESGGGLVQPGGSLRLSCAASGFTFTDYAMSWVRQAPGKGLEWVAVISYDGSTYYSADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCSR"
    vh_suffix = "WGQGTLVTVSS"
    vl_seq = "DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSRSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIK"

    candidates = []
    print(f"[Entry 060c] Generating {args.num} topology-aware candidates")

    for i in range(args.num):
        cid = f"CAND_v3_{i:04d}"
        cdr3 = generate_structured_cdr3()
        candidates.append({
            "id": cid,
            "heavy_chain": vh_prefix + cdr3 + vh_suffix,
            "light_chain": vl_seq,
            "cdr3": cdr3
        })
        print(f"  [+] {cid}: {cdr3}")

    with open(args.out, "w") as f:
        json.dump(candidates, f, indent=2)

if __name__ == "__main__":
    main()
