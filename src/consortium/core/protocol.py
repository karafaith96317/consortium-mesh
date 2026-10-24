"""Protocol data structures: directives, candidate profiles, and state deltas."""
from dataclasses import dataclass, field
from typing import Dict, List, Set

@dataclass
class Directive:
    epoch: int
    goal_id: str
    alignment_vector: List[float]
    sub_tasks: Dict[str, str]
    completed_tasks: Set[str] = field(default_factory=set)
    approvals: Set[str] = field(default_factory=set)

@dataclass(frozen=True)
class CandidateProfile:
    candidate_id: str
    compute_power: float
    ethics_score: float
    primary_skill: str  # "HEAVY_COMPUTE", "FAST_INGEST", "AUDIT_SAFETY"
    mutual_aid_capacity: float
