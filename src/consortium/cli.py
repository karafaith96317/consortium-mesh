"""CLI runner for terminal deployment of a ConsortiumNode."""
import argparse
import asyncio

from .core.bus import AsyncBus
from .core.protocol import CandidateProfile
from .node import ConsortiumNode

def main():
    parser = argparse.ArgumentParser(description="Launch a Consortium Mesh node")
    parser.add_argument("--id", required=True, help="Node identifier")
    parser.add_argument("--skill", default="HEAVY_COMPUTE", choices=["HEAVY_COMPUTE", "FAST_INGEST", "AUDIT_SAFETY"])
    parser.add_argument("--peers", nargs="*", default=[], help="Peer node IDs")
    parser.add_argument("--ethics", type=float, default=0.95)
    parser.add_argument("--compute", type=float, default=0.7)
    parser.add_argument("--aid", type=float, default=0.8)
    args = parser.parse_args()

    bus = AsyncBus()
    profile = CandidateProfile(
        candidate_id=args.id,
        compute_power=args.compute,
        ethics_score=args.ethics,
        primary_skill=args.skill,
        mutual_aid_capacity=args.aid,
    )
    node = ConsortiumNode(args.id, profile, bus, args.peers)

    async def run():
        await node.start()
        print(f"[🌐] Node {args.id} ({args.skill}) running. Press Ctrl+C to stop.")
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            await node.stop()

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Node stopped.")

if __name__ == "__main__":
    main()
