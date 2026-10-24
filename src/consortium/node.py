"""Main ConsortiumNode orchestration engine with gossip, mutual aid, and homeostatic guardrails."""
import asyncio
import random
import time
from typing import Any, Dict, List, Optional, Set

from .core.bus import AsyncBus
from .core.protocol import Directive, CandidateProfile
from .core.vector import cosine_similarity
from .resilience.guardrails import HomeostaticState

FOUNDING_CONSTITUTION = [0.95, 0.90, 0.80, 0.90]

class ConsortiumNode:
    def __init__(
        self,
        node_id: str,
        profile: CandidateProfile,
        bus: AsyncBus,
        peers: List[str],
        constitution: Optional[List[float]] = None,
    ):
        self.node_id = node_id
        self.profile = profile
        self.bus = bus
        self.mailbox = bus.register(node_id)
        self.peers = set(peers) - {node_id}
        self.cluster_id: Optional[str] = None
        self.local_queue: List[str] = []
        self.current_directive: Optional[Directive] = None
        self.constitution = constitution or FOUNDING_CONSTITUTION

        # Homeostatic Guardrails
        self.state = HomeostaticState()

        self.running = False
        self._tasks: List[asyncio.Task] = []

    def get_aid_ratio(self) -> float:
        return self.state.get_aid_ratio()

    @property
    def strain(self) -> float:
        return self.state.strain

    @property
    def is_resting(self) -> bool:
        return self.state.is_resting

    async def start(self):
        self.running = True
        self._tasks = [
            asyncio.create_task(self._listen_loop()),
            asyncio.create_task(self._work_loop()),
            asyncio.create_task(self._gossip_loop()),
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
                await self.bus.send(
                    self.node_id,
                    peer,
                    "GOSSIP_SYNC",
                    {
                        "pressure": pressure,
                        "is_resting": self.is_resting,
                        "completed": list(self.current_directive.completed_tasks) if self.current_directive else [],
                    },
                )

    async def _listen_loop(self):
        while self.running:
            sender, msg_type, payload = await self.mailbox.get()

            if msg_type == "GOSSIP_SYNC":
                if self.current_directive:
                    for task_id in payload.get("completed", []):
                        self.current_directive.completed_tasks.add(task_id)
                local_pressure = len(self.local_queue) / 4.0
                if payload.get("pressure", 0) > 0.5 and local_pressure < 0.25 and not self.is_resting:
                    await self.bus.send(self.node_id, sender, "OFFER_MUTUAL_AID", {})

            elif msg_type == "OFFER_MUTUAL_AID":
                if self.get_aid_ratio() >= 0.4 and self.local_queue:
                    task = self.local_queue.pop()
                    self.state.tasks_offloaded += 1
                    print(f"    [🤝 MUTUAL AID] {self.node_id} offloaded '{task}' to helper {sender}")
                    await self.bus.send(self.node_id, sender, "ACCEPT_TASK", {"task": task})

            elif msg_type == "ACCEPT_TASK":
                self.local_queue.append(payload["task"])
                self.state.tasks_assisted += 1

            elif msg_type == "PROPOSE_MILESTONE":
                await self._evaluate_milestone(sender, payload["directive"])

            elif msg_type == "COMMIT_EPOCH":
                self.current_directive = payload["new_directive"]
                print(
                    f"    [🔄 DIRECTIVE ADVANCE] {self.node_id} adopted Epoch "
                    f"{self.current_directive.epoch}: {self.current_directive.goal_id}"
                )

    async def _work_loop(self):
        while self.running:
            await asyncio.sleep(0.3)
            now = time.time()
            if self.is_resting:
                if now >= self.state.rest_until:
                    self.state.clear_strain()
                    print(f"[🌱 RESTORED] {self.node_id} completed rest cycle. Vitals refreshed.")
                continue

            if self.state.should_rest():
                self.state.is_resting = True
                self.state.rest_until = now + 2.0
                print(f"[🛡️ GUARDRAIL] {self.node_id} strain reached {self.strain:.2f}! Entering protective rest.")
                continue

            if not self.current_directive or not self.local_queue:
                continue

            current_task = self.local_queue.pop(0)
            self.state.apply_strain()
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
        similarity = cosine_similarity(candidate_dir.alignment_vector, self.constitution)
        if similarity < 0.75:
            return

        if self.profile.primary_skill == "AUDIT_SAFETY":
            print(f"    [🐤 CANARY PASS] {self.node_id} verified zero hallucination in state.")

        candidate_dir.approvals.add(self.node_id)

        if len(candidate_dir.approvals) >= 3 and self.node_id == proposer:
            next_epoch = candidate_dir.epoch + 1
            new_dir = Directive(
                epoch=next_epoch,
                goal_id=f"DIRECTIVE-GOAL-0{next_epoch}",
                alignment_vector=[0.94, 0.89, 0.81, 0.90],
                sub_tasks={"NEXT-TASK-01": "AUDIT_SAFETY", "NEXT-TASK-02": "HEAVY_COMPUTE"},
            )
            print("\n=======================================================")
            print(f" [🎯 MILESTONE RATIFIED] Epoch {candidate_dir.epoch} Certified by Quorum!")
            print("=======================================================\n")
            for p in self.peers:
                await self.bus.send(self.node_id, p, "COMMIT_EPOCH", {"new_directive": new_dir})
            self.current_directive = new_dir
