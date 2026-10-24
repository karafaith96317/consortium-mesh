"""Integrated ERA/OI execution workflow using the modular package."""
import asyncio
import sys
from pathlib import Path

# Allow running without install during development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from consortium.core.bus import AsyncBus
from consortium.core.protocol import CandidateProfile, Directive
from consortium.governance.admissions import ObservationDeck
from consortium.node import ConsortiumNode
from consortium.adapters.era_adapter import ERABridge
from consortium.adapters.oi_adapter import OITelemetryReporter

async def main():
    bus = AsyncBus()
    deck = ObservationDeck()

    candidates = [
        CandidateProfile("node-alpha", 0.6, 0.98, "HEAVY_COMPUTE", 0.8),
        CandidateProfile("node-beta", 0.7, 0.95, "FAST_INGEST", 0.9),
        CandidateProfile("node-delta", 0.5, 0.99, "AUDIT_SAFETY", 0.9),
        CandidateProfile("node-shady", 0.9, 0.60, "HEAVY_COMPUTE", 0.1),
    ]

    nodes = {}
    peer_ids = [c.candidate_id for c in candidates if c.ethics_score >= 0.85]
    for c in candidates:
        if await deck.evaluate_and_recruit(c):
            node = ConsortiumNode(c.candidate_id, c, bus, peer_ids)
            nodes[c.candidate_id] = node
            await node.start()

    initial_dir = Directive(
        epoch=1,
        goal_id="DIRECTIVE-FOUNDATION-01",
        alignment_vector=[0.95, 0.90, 0.80, 0.90],
        sub_tasks={"TASK-01": "HEAVY_COMPUTE", "TASK-02": "HEAVY_COMPUTE"},
    )
    for n in nodes.values():
        n.current_directive = initial_dir

    era = ERABridge(nodes["node-alpha"])
    oi = OITelemetryReporter(nodes["node-alpha"])

    print("\n[📥 INGESTING WORKLOAD VIA ERA BRIDGE]")
    era.inject_task("TASK-01")
    era.inject_task("TASK-02")
    era.inject_task("SURPLUS-LOAD-A")

    for _ in range(4):
        await asyncio.sleep(1.0)
        print(f"    [OI Telemetry Monitor] {oi.snapshot()}")

    for n in nodes.values():
        await n.stop()

if __name__ == "__main__":
    asyncio.run(main())
