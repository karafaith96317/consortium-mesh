"""Consortium Mesh — Autonomous multi-agent gossip consortium with homeostatic guardrails."""

from .node import ConsortiumNode
from .core.bus import AsyncBus
from .core.protocol import Directive, CandidateProfile
from .governance.admissions import ObservationDeck
from .adapters.era_adapter import ERABridge
from .adapters.oi_adapter import OITelemetryReporter

__all__ = [
    "ConsortiumNode",
    "AsyncBus",
    "Directive",
    "CandidateProfile",
    "ObservationDeck",
    "ERABridge",
    "OITelemetryReporter",
]

__version__ = "0.1.0"
