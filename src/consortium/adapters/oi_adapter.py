"""OI telemetry reporter for real-time health and operator monitoring."""
from typing import Any, Dict
from ..node import ConsortiumNode

class OITelemetryReporter:
    """Snapshots node vitals for Observer Intelligence dashboards."""
    def __init__(self, node: ConsortiumNode):
        self.node = node

    def snapshot(self) -> Dict[str, Any]:
        return {
            "node_id": self.node.node_id,
            "strain": round(self.node.strain, 2),
            "is_resting": self.node.is_resting,
            "aid_ratio": round(self.node.get_aid_ratio(), 2),
            "pending_queue": len(self.node.local_queue),
            "epoch": self.node.current_directive.epoch if self.node.current_directive else 0,
            "skill": self.node.profile.primary_skill,
        }
