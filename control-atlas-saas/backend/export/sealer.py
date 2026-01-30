import hashlib

class ForensicSealer:
    @staticmethod
    def canonical_serialize(atoms_list) -> str:
        """Generates a bit-stable string of coordinates (Chain-Seq-Name sorted)."""
        sorted_atoms = sorted(atoms_list, key=lambda a: (a.chain, a.res_seq, a.atom_name))
        return "".join([f"{a.chain}{a.res_seq}{a.atom_name}{a.pos[0]:.3f}{a.pos[1]:.3f}{a.pos[2]:.3f}" 
                        for a in sorted_atoms])

    @staticmethod
    def generate_hash(canonical_str: str) -> str:
        return hashlib.sha256(canonical_str.encode()).hexdigest()

    @staticmethod
    def seal_pdb(pdb_body: str, audit_id: str, verdict: str, coord_hash: str) -> str:
        header = [
            f"REMARK 900 TOSCANINI FORENSIC SEAL v14.0",
            f"REMARK 900 AUDIT_ID: {audit_id}",
            f"REMARK 901 VERDICT: {verdict}",
            f"REMARK 902 COORD_HASH: {coord_hash}",
            f"REMARK 903 STATUS: NOTARIZED_SOVEREIGN",
            "REMARK 903 " + ("="*40)
        ]
        return "\n".join(header) + "\n" + pdb_body

    @staticmethod
    def verify_seal(atoms_list, claimed_hash: str) -> bool:
        """Recalculates the seal from atom objects and compares to claim."""
        actual_hash = ForensicSealer.generate_hash(ForensicSealer.canonical_serialize(atoms_list))
        return actual_hash == claimed_hash
