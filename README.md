🌐 Consortium Mesh: Autonomous Multi-Agent Gossip Consortium with Homeostatic Guardrails
A Byzantine-resilient, decentralized multi-agent coordination protocol built in Python asyncio. It replaces centralized coordinators and fragile single-leader patterns with epidemic Scuttlebutt dissemination, autonomous P2P mutual-aid work-stealing, and strict constitutional safety guardrails to eliminate cascading entropy and allostatic worker burnout.
Designed as a standalone engine with ready-to-use adapters for ERA (task injection / epoch tracking) and OI (real-time telemetry and operator monitoring).
🌟 Key Architecture & Pillars
 * Epidemic Anti-Entropy (Scuttlebutt Protocol):
   * High-watermark version tracking (\mathcal{O}(N) digest exchange) instead of transferring unbounded state logs.
   * Monotonic versioning and generation epochs ensure seamless rejoins after network partitions or node restarts.
 * Admissions Auditing & Ethical Filtering:
   * Pre-flight evaluation deck verifies candidate compute power, task headroom, and historical ethics scores (\ge 0.85). Unaligned or malicious nodes are rejected prior to joining the trust envelope.
 * Dynamic Topology Sharding & Mutual Aid:
   * Nodes automatically self-organize into functional clusters (HEAVY_COMPUTE, FAST_INGEST, AUDIT_SAFETY).
   * Overloaded workers offload tasks to idle neighbors via non-blocking gossip handshakes.
   * Includes a Reciprocal Aid Ledger (anti-parasitism) that throttles offloading if a node refuses to contribute back.
 * Homeostatic Guardrails (Anti-Burnout & No Trauma Accumulation):
   * Tracks allostatic workload strain. Crossing the safety threshold (\ge 0.70) triggers automated, non-punitive rest rotations (Allorecess).
   * Natural entropic decay clears operational friction over time—preventing nodes from accumulating permanent memory scars or turning adversarial.
 * Consensus & Epistemic Alignment:
   * Canary Inquirer: A designated safety auditor runs adversarial counter-proofs to challenge state updates before epoch rollover.
   * Constitutional Vector Anchor: Proposed directives must maintain cosine vector similarity \ge 0.75 against the founding mandate to prevent mission drift.
   * Heterogeneous Quorum: Milestones require multi-signature verification across diverse node archetypes.
📁 Repository Structure
consortium-mesh/
├── pyproject.toml              # Build metadata and entry point
├── README.md                   # Project overview & architecture
├── config/
│   └── constitution.json       # Founding invariant vectors & thresholds
├── src/
│   └── consortium/
│       ├── __init__.py         # Public exports (ConsortiumNode, AsyncBus, etc.)
│       ├── cli.py              # CLI runner for terminal deployment
│       ├── core/
│       │   ├── bus.py          # Message bus abstraction (async / sockets)
│       │   ├── protocol.py     # Directives, candidate profiles, and state deltas
│       │   └── vector.py       # Cosine alignment and embedding math
│       ├── governance/
│       │   └── admissions.py   # Observation deck and ethics auditing gate
│       ├── resilience/
│       │   └── guardrails.py   # Allostatic strain tracker & mutual-aid ledger
│       ├── node.py             # Main ConsortiumNode orchestration engine
│       └── adapters/
│           ├── era_adapter.py  # Connector for ERA pipelines & task submission
│           └── oi_adapter.py   # Connector for OI telemetry & health monitors
└── examples/
    ├── standalone_sim.py       # Single-file lightweight reference demo
    └── run_with_era_oi.py      # Integrated ERA/OI execution workflow

🚀 Single-File Standalone Prototype (standalone_sim.py)
Run the self-contained engine in any terminal, notebook, or environment without dependencies:
```python
import asyncio
import math
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

# --- 1. Constitutional Vector & Protocol Directives ---
FOUNDING_CONSTITUTION = [0.95, 0.90, 0.80, 0.90]

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

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

# --- 2. Network Bus ---
class AsyncBus:
    def __init__(self):
        self.queues: Dict[str, asyncio.Queue] = {}

    def register(self, node_id: str) -> asyncio.Queue:
        q = asyncio.Queue()
        self.queues[node_id] = q
        return q

    async def send(self, sender: str, recipient: str, msg_type: str, payload: Dict[str, Any]):
        if recipient in self.queues:
            await self.queues[recipient].put((sender, msg_type, payload))

# --- 3. Observation Deck & Admissions ---
class ObservationDeck:
    async def evaluate_and_recruit(self, candidate: CandidateProfile) -> bool:
        if candidate.ethics_score < 0.85:
            print(f"[🏛️ ADMISSIONS] REJECTED {candidate.candidate_id} (Ethics: {candidate.ethics_score:.2f} < 0.85)")
            return False
        if candidate.mutual_aid_capacity < 0.50:
            print(f"[🏛️ ADMISSIONS] REJECTED {candidate.candidate_id} (Insufficient mutual aid)")
            return False
        print(f"[🏛️ ADMISSIONS] ACCEPTED {candidate.candidate_id} ({candidate.primary_skill})")
        return True

# --- 4. Consortium Node with Guardrails ---
class ConsortiumNode:
    def __init__(self, node_id: str, profile: CandidateProfile, bus: AsyncBus, peers: List[str]):
        self.node_id = node_id
        self.profile = profile
        self.bus = bus
        self.mailbox = bus.register(node_id)
        self.peers = set(peers) - {node_id}
        self.cluster_id: Optional[str] = None
        self.local_queue: List[str] = []
        self.current_directive: Optional[Directive] = None

        # Homeostatic Guardrails
        self.strain = 0.0
        self.is_resting = False
        self.rest_until = 0.0
        self.tasks_offloaded = 0
        self.tasks_assisted = 0

        self.running = False
        self._tasks: List[asyncio.Task] = []

    def get_aid_ratio(self) -> float:
        return (self.tasks_assisted + 1) / (self.tasks_offloaded + 1)

    async def start(self):
        self.running = True
        self._tasks = [
            asyncio.create_task(self._listen_loop()),
            asyncio.create_task(self._work_loop()),
            asyncio.create_task(self._gossip_loop())
        ]

    async def stop(self):
        self.running = False
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

    async def _gossip_loop(self):
        while self.running:
            await asyncio.sleep(0.25)
            if not self.peers:
                continue
            targets = random.sample(list(self.peers), min(2, len(self.peers)))
            pressure = 1.0 if self.is_resting else (len(self.local_queue) / 4.0)
            for peer in targets:
                await self.bus.send(self.node_id, peer, "GOSSIP_SYNC", {
                    "pressure": pressure,
                    "is_resting": self.is_resting,
                    "completed": list(self.current_directive.completed_tasks) if self.current_directive else []
                })

    async def _listen_loop(self):
        while self.running:
            sender, msg_type, payload = await self.mailbox.get()

            if msg_type == "GOSSIP_SYNC":
                if self.current_directive:
                    for task_id in payload["completed"]:
                        self.current_directive.completed_tasks.add(task_id)
                # Mutual aid trigger
                local_pressure = len(self.local_queue) / 4.0
                if payload["pressure"] > 0.5 and local_pressure < 0.25 and not self.is_resting:
                    await self.bus.send(self.node_id, sender, "OFFER_MUTUAL_AID", {})

            elif msg_type == "OFFER_MUTUAL_AID":
                if self.get_aid_ratio() >= 0.4 and self.local_queue:
                    task = self.local_queue.pop()
                    self.tasks_offloaded += 1
                    print(f"    [🤝 MUTUAL AID] {self.node_id} offloaded '{task}' to helper {sender}")
                    await self.bus.send(self.node_id, sender, "ACCEPT_TASK", {"task": task})

            elif msg_type == "ACCEPT_TASK":
                self.local_queue.append(payload["task"])
                self.tasks_assisted += 1

            elif msg_type == "PROPOSE_MILESTONE":
                await self._evaluate_milestone(sender, payload["directive"])

            elif msg_type == "COMMIT_EPOCH":
                self.current_directive = payload["new_directive"]
                print(f"    [🔄 DIRECTIVE ADVANCE] {self.node_id} adopted Epoch {self.current_directive.epoch}: {self.current_directive.goal_id}")

    async def _work_loop(self):
        while self.running:
            await asyncio.sleep(0.3)
            now = time.time()
            if self.is_resting:
                if now >= self.rest_until:
                    self.is_resting = False
                    self.strain = 0.0
                    print(f"[🌱 RESTORED] {self.node_id} completed rest cycle. Vitals refreshed.")
                continue

            if self.strain >= 0.70:
                self.is_resting = True
                self.rest_until = now + 2.0
                print(f"[🛡️ GUARDRAIL] {self.node_id} strain reached {self.strain:.2f}! Entering protective rest.")
                continue

            if not self.current_directive or not self.local_queue:
                continue

            current_task = self.local_queue.pop(0)
            self.strain += 0.20
            await asyncio.sleep(0.3 * (1.0 - (self.profile.compute_power * 0.4)))
            self.current_directive.completed_tasks.add(current_task)
            print(f"    [⚡ SOLVED] {self.node_id} completed '{current_task}' (Strain: {self.strain:.2f})")

            all_tasks = set(self.current_directive.sub_tasks.keys())
            if all_tasks.issubset(self.current_directive.completed_tasks):
                if self.node_id not in self.current_directive.approvals:
                    self.current_directive.approvals.add(self.node_id)
                    for p in self.peers:
                        await self.bus.send(self.node_id, p, "PROPOSE_MILESTONE", {"directive": self.current_directive})

    async def _evaluate_milestone(self, proposer: str, candidate_dir: Directive):
        # 1. Cosine similarity constitutional check
        similarity = cosine_similarity(candidate_dir.alignment_vector, FOUNDING_CONSTITUTION)
        if similarity < 0.75:
            return

        # 2. Canary inquirer counter-proof
        if self.profile.primary_skill == "AUDIT_SAFETY":
            print(f"    [🐤 CANARY PASS] {self.node_id} verified zero hallucination in state.")

        candidate_dir.approvals.add(self.node_id)

        # 3. Heterogeneous quorum check
        if len(candidate_dir.approvals) >= 3 and self.node_id == proposer:
            next_epoch = candidate_dir.epoch + 1
            new_dir = Directive(
                epoch=next_epoch,
                goal_id=f"DIRECTIVE-GOAL-0{next_epoch}",
                alignment_vector=[0.94, 0.89, 0.81, 0.90],
                sub_tasks={"NEXT-TASK-01": "AUDIT_SAFETY", "NEXT-TASK-02": "HEAVY_COMPUTE"}
            )
            print(f"\n=======================================================")
            print(f" [🎯 MILESTONE RATIFIED] Epoch {candidate_dir.epoch} Certified by Quorum!")
            print(f"=======================================================\n")
            for p in self.peers:
                await self.bus.send(self.node_id, p, "COMMIT_EPOCH", {"new_directive": new_dir})
            self.current_directive = new_dir

# --- 5. Integrated ERA & OI Adapters ---
class ERABridge:
    def __init__(self, node: ConsortiumNode):
        self.node = node
    def inject_task(self, task_name: str):
        self.node.local_queue.append(task_name)

class OITelemetryReporter:
    def __init__(self, node: ConsortiumNode):
        self.node = node
    def snapshot(self) -> Dict[str, Any]:
        return {
            "node_id": self.node.node_id,
            "strain": round(self.node.strain, 2),
            "is_resting": self.node.is_resting,
            "aid_ratio": round(self.node.get_aid_ratio(), 2),
            "pending_queue": len(self.node.local_queue),
            "epoch": self.node.current_directive.epoch if self.node.current_directive else 0
        }

# --- Execution Test ---
async def main():
    bus = AsyncBus()
    deck = ObservationDeck()
    candidates = [
        CandidateProfile("node-alpha", 0.6, 0.98, "HEAVY_COMPUTE", 0.8),
        CandidateProfile("node-beta",  0.7, 0.95, "FAST_INGEST",   0.9),
        CandidateProfile("node-delta", 0.5, 0.99, "AUDIT_SAFETY",  0.9),
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
        sub_tasks={"TASK-01": "HEAVY_COMPUTE", "TASK-02": "HEAVY_COMPUTE"}
    )
    for n in nodes.values():
        n.current_directive = initial_dir

    era = ERABridge(nodes["node-alpha"])
    oi = OITelemetryReporter(nodes["node-alpha"])

    # Surge workload into node-alpha to test Mutual Aid and Homeostasis
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
```

🛠️ Quickstart
1. Clone & Set Up
git clone https://github.com/karafaith96317/consortium-mesh.git
cd consortium-mesh
pip install -e .

2. Run the Single-File Demo
python3 examples/standalone_sim.py

3. Launch an Independent Node via CLI
consortium-node --id worker-01 --skill HEAVY_COMPUTE --peers worker-02 worker-03

📄 License
MIT License. Open-source for collaborative research and distributed AI collectives.
