"""ERA bridge for task injection and epoch tracking."""
from ..node import ConsortiumNode

class ERABridge:
    """Injects tasks into a ConsortiumNode from an ERA pipeline."""
    def __init__(self, node: ConsortiumNode):
        self.node = node

    def inject_task(self, task_name: str):
        self.node.local_queue.append(task_name)

    def current_epoch(self) -> int:
        if self.node.current_directive:
            return self.node.current_directive.epoch
        return 0
