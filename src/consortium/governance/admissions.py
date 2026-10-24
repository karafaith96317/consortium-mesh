"""Observation deck and ethics auditing gate."""
from ..core.protocol import CandidateProfile

class ObservationDeck:
    """Pre-flight evaluation of candidate nodes against constitutional thresholds."""
    def __init__(self, ethics_min: float = 0.85, aid_min: float = 0.50):
        self.ethics_min = ethics_min
        self.aid_min = aid_min

    async def evaluate_and_recruit(self, candidate: CandidateProfile) -> bool:
        if candidate.ethics_score < self.ethics_min:
            print(f"[🏛️ ADMISSIONS] REJECTED {candidate.candidate_id} (Ethics: {candidate.ethics_score:.2f} < {self.ethics_min})")
            return False
        if candidate.mutual_aid_capacity < self.aid_min:
            print(f"[🏛️ ADMISSIONS] REJECTED {candidate.candidate_id} (Insufficient mutual aid)")
            return False
        print(f"[🏛️ ADMISSIONS] ACCEPTED {candidate.candidate_id} ({candidate.primary_skill})")
        return True
