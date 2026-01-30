import hashlib, os, tempfile, numpy as np
from Bio.PDB import PDBParser, MMCIFParser
from .structure_object import StructureObject, Atom, ConfidenceSidecar

class IngestionProcessor:
    @staticmethod
    def run(file_content: bytes, filename: str, generator: str, intent: str = "General") -> StructureObject:
        ext = filename.split(".")[-1].lower()
        pdb_string = file_content.decode("utf-8", errors="replace")
        audit_id = hashlib.sha256(file_content).hexdigest()[:16]
        
        with tempfile.NamedTemporaryFile(suffix=f".{ext}", mode='w', delete=False) as tf:
            tf.write(pdb_string); t_path = tf.name
        
        parser = PDBParser(QUIET=True) if ext == "pdb" else MMCIFParser(QUIET=True)
        struct = parser.get_structure("CLAIM", t_path); os.remove(t_path)
        
        atoms, ligands, plddts = [], [], []
        for model in struct:
            for chain in model:
                for residue in chain:
                    is_lig = residue.get_id()[0].strip() != ""
                    for atom in residue:
                        if atom.element == "H": continue 
                        
                        # Extract pLDDT from bfactor (ML Standard)
                        conf_val = float(atom.get_bfactor())
                        if not is_lig: plddts.append(conf_val)
                        
                        a_obj = Atom(
                            res_name=residue.get_resname(), res_seq=residue.get_id()[1],
                            chain=chain.id, atom_name=atom.get_name(), element=atom.element,
                            pos=tuple(float(x) for x in atom.get_coord()),
                            plddt=conf_val
                        )
                        if is_lig: ligands.append(a_obj)
                        else: atoms.append(a_obj)
        
        # Calculate Confidence Sidecar
        mean_plddt = float(np.mean(plddts)) if plddts else 0.0; mean_plddt = mean_plddt * 100 if 0 < mean_plddt <= 1.0 else mean_plddt
        sidecar = ConfidenceSidecar(
            mean_plddt=mean_plddt,
            is_low_confidence=(mean_plddt < 70.0),
            metrics={"plddt_array_len": len(plddts)}
        )
        
        return StructureObject(
            audit_id=audit_id, source_model=generator, intent_profile=intent,
            atoms=tuple(atoms), ligands=tuple(ligands), confidence=sidecar,
            metadata={"filename": filename}
        )
