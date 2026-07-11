import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

TOPIC_THRESHOLD = 0.25
HISTORY_THRESHOLD = 0.9

_query_history: list[np.ndarray] = []

_cache = Path(__file__).parent.parent / ".model_cache"
_cache.mkdir(exist_ok=True)
_local_files_only = (
    _cache / "models--sentence-transformers--all-MiniLM-L6-v2"
).exists()
_model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    cache_folder=str(_cache),
    local_files_only=_local_files_only,
)

_person_path = Path(__file__).parent.parent / "PERSON.json"
_person = json.loads(_person_path.read_text())

# neutral topic embeddings — no sentiment framing
_like_topics: np.ndarray = _model.encode(_person["likes"])
_dislike_topics: np.ndarray = _model.encode(_person["dislikes"])

# sentiment templates from weak to strong
_positive_templates: np.ndarray = _model.encode(
    [
        "I like this",
        "this is pretty good",
        "I enjoy this",
        "I'm a fan of this",
        "I love this",
        "this is wonderful",
        "this is amazing",
        "I absolutely adore this",
        "I'm obsessed with this",
    ]
)
_negative_templates: np.ndarray = _model.encode(
    [
        "this is not great",
        "I don't really like this",
        "I dislike this",
        "I don't enjoy this",
        "I hate this",
        "this is terrible",
        "I can't stand this",
        "I despise this",
        "I loathe this",
        "I absolutely abhor this",
    ]
)


def _max_sim(embeddings: np.ndarray, query: np.ndarray) -> float:
    sims = np.dot(embeddings, query) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query)
    )
    return float(np.max(sims))


def reset_history() -> None:
    _query_history.clear()


def compare(text: str) -> float | None | str:
    """
    Returns a signed effect in [-1, 1]:
      positive → user agrees with person → slow down
      negative → user disagrees with person → speed up
      None → no relevant topic detected
    Magnitude reflects topic relevance × sentiment strength.
    """
    query = _model.encode(text)

    if _query_history:
        history = np.stack(_query_history)
        if _max_sim(history, query) > HISTORY_THRESHOLD:
            return "too_similar"
    _query_history.append(query)

    like_sim = _max_sim(_like_topics, query)
    dislike_sim = _max_sim(_dislike_topics, query)
    best_topic_sim = max(like_sim, dislike_sim)

    if best_topic_sim < TOPIC_THRESHOLD:
        return None

    topic_is_like = like_sim >= dislike_sim

    pos_score = _max_sim(_positive_templates, query)
    neg_score = _max_sim(_negative_templates, query)
    # positive = user expressed positive sentiment, negative = negative sentiment
    sentiment = pos_score - neg_score

    # for a like: positive sentiment → agree; negative → disagree
    # for a dislike: negative sentiment → agree; positive → disagree
    direction = sentiment if topic_is_like else -sentiment

    effect = float(np.clip(direction * best_topic_sim * 6, -1.0, 1.0))
    return effect
