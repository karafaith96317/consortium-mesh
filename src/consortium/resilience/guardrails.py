"""Allostatic strain tracker and reciprocal aid ledger."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class HomeostaticState:
    strain: float = 0.0
    is_resting: bool = False
    rest_until: float = 0.0
    tasks_offloaded: int = 0
    tasks_assisted: int = 0

    def get_aid_ratio(self) -> float:
        """Reciprocal aid ratio to prevent parasitism."""
        return (self.tasks_assisted + 1) / (self.tasks_offloaded + 1)

    def should_rest(self, threshold: float = 0.70) -> bool:
        return self.strain >= threshold and not self.is_resting

    def apply_strain(self, amount: float = 0.20):
        if not self.is_resting:
            self.strain = min(1.0, self.strain + amount)

    def clear_strain(self):
        self.strain = 0.0
        self.is_resting = False
