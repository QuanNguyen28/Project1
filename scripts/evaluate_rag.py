from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from embeddings.utils.gemini_embed import embed_query
from src.db.models import JobDescription
from src.db.session import SessionLocal
from src.services.retriever_service import retrieve_hybrid


def evaluate(mode: str, sample_size: int, top_k: int) -> dict:
    db = SessionLocal()
    try:
        rows = (
            db.query(JobDescription.jd_id, JobDescription.title)
            .filter(JobDescription.source_name.isnot(None))
            .order_by(JobDescription.jd_id)
            .limit(sample_size)
            .all()
        )
    finally:
        db.close()

    reciprocal_ranks = []
    recalls = []
    unique_ratios = []
    misses = []
    for jd_id, title in rows:
        vector = None if mode == "lexical" else embed_query(title)
        results = retrieve_hybrid(
            title,
            vector,
            top_k,
            mode=mode,
            max_chunks_per_jd=1,
        )
        ids = [item.jd_id for item in results]
        rank = ids.index(jd_id) + 1 if jd_id in ids else None
        recalls.append(1.0 if rank else 0.0)
        reciprocal_ranks.append(1.0 / rank if rank else 0.0)
        unique_ratios.append(len(set(ids)) / len(ids) if ids else 0.0)
        if rank is None:
            misses.append({"jd_id": jd_id, "query": title, "returned": ids})

    count = len(rows) or 1
    return {
        "mode": mode,
        "queries": len(rows),
        f"recall_at_{top_k}": round(sum(recalls) / count, 4),
        "mrr": round(sum(reciprocal_ranks) / count, 4),
        "unique_jd_ratio": round(sum(unique_ratios) / count, 4),
        "misses": misses,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate RAG retrieval on real JD titles")
    parser.add_argument("--mode", choices=("hybrid", "dense", "lexical"), default="hybrid")
    parser.add_argument("--sample-size", type=int, default=15)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--output")
    args = parser.parse_args()
    report = evaluate(args.mode, args.sample_size, args.top_k)
    encoded = json.dumps(report, ensure_ascii=False, indent=2)
    print(encoded)
    if args.output:
        Path(args.output).write_text(encoded + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
