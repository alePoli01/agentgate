import sys
import logging

logger = logging.getLogger("agentgate")

def run_arbiter(query: str, filepath: str) -> None:
    """Check if a file passes the semantic relevance threshold using the RAG engine."""
    try:
        import rag
        passed, score = rag.check_arbiter(query, filepath)
        if passed:
            print(f"[ARBITER APPROVED] {filepath} is relevant. (Score: {score:.2f})")
        else:
            print(f"[ARBITER BLOCKED] {filepath} is irrelevant. (Score: {score:.2f} < 0.3)")
            print("Access denied to protect context window. Try using semantic_search instead.")
    except Exception as e:
        logger.error("Arbiter failed: %s", e)
        print(f"[ERROR] Arbiter failed: {e}")
        sys.exit(1)
    
    sys.exit(0)
