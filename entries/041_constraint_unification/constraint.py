from dataclasses import dataclass

@dataclass
class Constraint:
    layer: str
    parameter: str
    threshold: float
    actual: float
    margin: float
    status: str              # PASS, FAIL, WARNING
    collapses_space: bool
    provenance: dict
