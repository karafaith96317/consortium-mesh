"""Constitutional vector alignment math."""
import math
from typing import List

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Compute cosine similarity between two vectors. Returns 0.0 on degenerate cases."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must be the same length")
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
