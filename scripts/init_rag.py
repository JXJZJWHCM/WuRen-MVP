import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.rag_engine import RAGEngine, RAG_AVAILABLE


def main() -> int:
    if not RAG_AVAILABLE:
        print("[init_rag] RAG dependencies unavailable, skip initialization.")
        return 0

    data_dir = ROOT / "data"
    knowledge_dir = data_dir / "knowledge"
    skills_dir = data_dir / "skills"
    vector_dir = data_dir / "vector_db"
    models_dir = data_dir / "models"

    engine = RAGEngine(persist_directory=str(vector_dir), cache_directory=str(models_dir))
    if not engine.initialize():
        print("[init_rag] Failed to initialize RAG engine.")
        return 0

    force = os.getenv("RAG_FORCE_REINDEX", "0").strip().lower() in ("1", "true", "yes", "y")
    try:
        existing_count = int(engine.collection.count()) if engine.collection else 0
    except Exception:
        existing_count = 0

    if existing_count > 0 and not force:
        print(f"[init_rag] Vector DB already initialized ({existing_count} chunks), skip reindex.")
        return 0

    indexed_dirs = []
    if knowledge_dir.exists():
        engine.index_directory(str(knowledge_dir))
        indexed_dirs.append(str(knowledge_dir))
    if skills_dir.exists():
        engine.index_directory(str(skills_dir))
        indexed_dirs.append(str(skills_dir))

    if not indexed_dirs:
        print("[init_rag] No knowledge directories found, skip indexing.")
        return 0

    try:
        final_count = int(engine.collection.count()) if engine.collection else 0
    except Exception:
        final_count = -1

    print(f"[init_rag] Indexed directories: {', '.join(indexed_dirs)}")
    print(f"[init_rag] Current vector chunks: {final_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
