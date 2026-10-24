"""Async message bus abstraction for gossip and mutual-aid handshakes."""
import asyncio
from typing import Any, Dict

class AsyncBus:
    """Simple in-process async bus. Replace with socket/gRPC transport for real networks."""
    def __init__(self):
        self.queues: Dict[str, asyncio.Queue] = {}

    def register(self, node_id: str) -> asyncio.Queue:
        q = asyncio.Queue()
        self.queues[node_id] = q
        return q

    async def send(self, sender: str, recipient: str, msg_type: str, payload: Dict[str, Any]):
        if recipient in self.queues:
            await self.queues[recipient].put((sender, msg_type, payload))
