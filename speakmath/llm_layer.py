
# llm_layer.py (stubbed LLM resolver)
from .semantic_map import SYNONYM_MAP, SEMANTIC_MAP

def resolve_phrase(phrase: str) -> str:
    """
    Resolve a verb phrase to a canonical operator token.
    First check direct mapping, then synonym map; otherwise return None
    indicating LLM should be consulted (stubbed).
    """
    key = phrase.lower().strip()
    if key in SEMANTIC_MAP:
        return SEMANTIC_MAP[key]
    if key in SYNONYM_MAP:
        return SYNONYM_MAP[key]
    # simple heuristics for patterns:
    if key.startswith("find the mean") or "mean" in key:
        return "OP_MEAN"
    if "average" in key:
        return "OP_MEAN"
    # No match: return None to indicate LLM fallback in real system
    return None
