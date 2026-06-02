import json
import re
from pathlib import Path
from typing import Any


KNOWLEDGE_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "regulation_knowledge"
)


KNOWLEDGE_FILE_BY_JURISDICTION = {
    "munich": "munich_lbk_knowledge.json",
    "germany": "munich_lbk_knowledge.json",
    "bavaria": "munich_lbk_knowledge.json",
}


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-zäöüß0-9\s/-]", " ", text)
    text = " ".join(text.split())
    return text


def tokenize(text: str) -> set[str]:
    stopwords = {
        "the", "and", "or", "of", "for", "to", "in", "a", "an", "is", "are",
        "with", "where", "as", "by", "be", "this", "that", "should",
        "der", "die", "das", "und", "oder", "mit", "für", "von", "im", "in",
        "zu", "ist", "sind", "ein", "eine", "einer", "eines", "werden"
    }

    words = normalize_text(text).split()

    return {
        word
        for word in words
        if len(word) > 2 and word not in stopwords
    }


def load_knowledge_base(jurisdiction: str) -> list[dict[str, Any]]:
    jurisdiction_key = (jurisdiction or "general").lower()

    file_name = KNOWLEDGE_FILE_BY_JURISDICTION.get(jurisdiction_key)

    if not file_name:
        return []

    file_path = KNOWLEDGE_DIR / file_name

    if not file_path.exists():
        return []

    return json.loads(file_path.read_text(encoding="utf-8"))


def score_chunk(query: str, chunk: dict[str, Any]) -> float:
    query_tokens = tokenize(query)

    searchable_text = " ".join(
        [
            chunk.get("title", ""),
            chunk.get("source", ""),
            chunk.get("text", ""),
            " ".join(chunk.get("keywords", [])),
            " ".join(chunk.get("related_requirements", [])),
        ]
    )

    chunk_tokens = tokenize(searchable_text)

    if not query_tokens or not chunk_tokens:
        return 0.0

    overlap = query_tokens.intersection(chunk_tokens)

    overlap_score = len(overlap) / max(len(query_tokens), 1)

    keyword_score = 0.0
    query_lower = normalize_text(query)

    for keyword in chunk.get("keywords", []):
        if normalize_text(keyword) in query_lower:
            keyword_score += 0.35

    return overlap_score + keyword_score


def retrieve_regulation_context(
    jurisdiction: str,
    queries: list[str],
    top_k: int = 5,
) -> list[dict[str, Any]]:
    knowledge_base = load_knowledge_base(jurisdiction)

    if not knowledge_base:
        return []

    scored_chunks = {}

    for query in queries:
        for chunk in knowledge_base:
            chunk_id = chunk.get("id")

            if not chunk_id:
                continue

            score = score_chunk(query, chunk)

            if score <= 0:
                continue

            if chunk_id not in scored_chunks or score > scored_chunks[chunk_id]["score"]:
                scored_chunks[chunk_id] = {
                    "score": score,
                    "chunk": chunk,
                    "matched_query": query,
                }

    ranked = sorted(
        scored_chunks.values(),
        key=lambda item: item["score"],
        reverse=True,
    )

    results = []

    for item in ranked[:top_k]:
        chunk = item["chunk"]

        results.append(
            {
                "id": chunk.get("id"),
                "title": chunk.get("title"),
                "jurisdiction": chunk.get("jurisdiction"),
                "source": chunk.get("source"),
                "text": chunk.get("text"),
                "related_requirements": chunk.get("related_requirements", []),
                "score": round(item["score"], 3),
                "matched_query": item["matched_query"],
            }
        )

    return results