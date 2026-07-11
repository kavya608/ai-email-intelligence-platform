"""
The AI intelligence engine.

This module is what makes the platform "understand" emails instead of just
storing them. It's built as a layered, hybrid system:

  1. Rule/keyword-based signals (fast, free, deterministic) — always run.
  2. Lightweight statistical summarization (TF-IDF sentence ranking) — always run.
  3. Optional LLM enhancement (Anthropic/OpenAI) — used only if an API key is
     configured, to sharpen categorization/summarization further.

This design means the whole platform works out of the box with zero API keys
and zero cost, and gets smarter automatically if you plug in an LLM key.
"""
import os
import re
from datetime import datetime
from typing import List, Dict, Tuple

from dateutil import parser as dateparser
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# ---------------------------------------------------------------------------
# Category keyword signals
# ---------------------------------------------------------------------------
CATEGORY_KEYWORDS = {
    "Urgent": [
        "urgent", "asap", "immediately", "right away", "critical",
        "emergency", "time-sensitive", "deadline today", "eod",
    ],
    "Action Needed": [
        "please send", "please review", "can you", "need you to",
        "action required", "waiting on", "follow up", "reply by",
        "approve", "sign off", "complete the", "submit",
    ],
    "Meeting": [
        "meeting", "call", "schedule", "calendar", "invite",
        "zoom", "teams link", "reschedule", "availability",
    ],
    "Informational": [
        "fyi", "newsletter", "update", "announcement", "summary",
        "no action needed", "heads up",
    ],
    "Spam-like": [
        "unsubscribe", "limited time offer", "click here", "winner",
        "free gift", "act now", "congratulations you", "% off",
    ],
}

# Weight per category when computing priority score
CATEGORY_WEIGHT = {
    "Urgent": 40,
    "Action Needed": 25,
    "Meeting": 15,
    "Informational": 5,
    "Spam-like": -20,
}

DEADLINE_PATTERN = re.compile(
    r"(by|before|due|no later than)\s+([A-Za-z0-9 ,]+?(?:\d{1,2}(st|nd|rd|th)?)?"
    r"(?:\s+\d{4})?)",
    re.IGNORECASE,
)

ACTION_VERBS = [
    "send", "review", "approve", "complete", "submit", "reply",
    "confirm", "update", "schedule", "prepare", "share", "sign",
    "finish", "provide", "attach", "call", "follow up",
]


def _score_categories(text: str) -> Dict[str, int]:
    """Count keyword hits per category in the given text (case-insensitive)."""
    lowered = text.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in lowered)
        if hits:
            scores[category] = hits
    return scores


def classify_email(subject: str, body: str) -> str:
    """
    Pick the single best category for an email based on keyword signal
    strength in the subject (weighted higher) and body.
    """
    subject_scores = _score_categories(subject)
    body_scores = _score_categories(body)

    combined: Dict[str, float] = {}
    for cat, hits in subject_scores.items():
        combined[cat] = combined.get(cat, 0) + hits * 2  # subject counts double
    for cat, hits in body_scores.items():
        combined[cat] = combined.get(cat, 0) + hits

    if not combined:
        return "Informational"

    return max(combined.items(), key=lambda kv: kv[1])[0]


def extract_action_items(body: str) -> List[str]:
    """
    Pull out sentences that look like actionable requests — i.e. contain an
    action verb near the start, or an imperative/"please ..." construction.
    """
    sentences = re.split(r"(?<=[.!?])\s+", body.strip())
    action_items = []

    for sentence in sentences:
        lowered = sentence.lower().strip()
        if not lowered:
            continue
        starts_with_please = lowered.startswith("please")
        has_action_verb = any(
            re.search(rf"\b{verb}\b", lowered) for verb in ACTION_VERBS
        )
        has_request_phrase = any(
            phrase in lowered
            for phrase in ["can you", "could you", "need you to", "make sure to"]
        )
        if starts_with_please or has_request_phrase or (
            has_action_verb and len(sentence.split()) < 40
        ):
            action_items.append(sentence.strip())

    # De-duplicate while preserving order
    seen = set()
    unique_items = []
    for item in action_items:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)

    return unique_items[:8]  # cap to keep it readable


def extract_deadlines(body: str) -> List[Dict]:
    """
    Find phrases like "by Friday", "before March 5th", "no later than 5pm"
    and attempt to resolve them to actual dates where possible.
    """
    deadlines = []
    for match in DEADLINE_PATTERN.finditer(body):
        raw_text = match.group(0).strip()
        date_fragment = match.group(2).strip()
        resolved_date = None
        try:
            resolved_date = dateparser.parse(
                date_fragment, fuzzy=True, default=datetime.utcnow()
            ).date().isoformat()
        except (ValueError, OverflowError):
            resolved_date = None

        deadlines.append({"text": raw_text, "date": resolved_date})

    return deadlines


def summarize(body: str, max_sentences: int = 3) -> str:
    """
    Lightweight extractive summarization using TF-IDF sentence scoring.
    No external model or API needed — works fully offline.
    """
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body.strip()) if s.strip()]

    if len(sentences) <= max_sentences:
        return body.strip()

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(sentences)
        # Score each sentence by the sum of its TF-IDF weights
        sentence_scores = np.asarray(tfidf_matrix.sum(axis=1)).ravel()
        top_indices = sentence_scores.argsort()[::-1][:max_sentences]
        top_indices_sorted = sorted(top_indices)  # keep original order
        summary = " ".join(sentences[i] for i in top_indices_sorted)
        return summary
    except ValueError:
        # e.g. body is all stopwords / too short for TF-IDF
        return " ".join(sentences[:max_sentences])


def extract_keywords(body: str, top_n: int = 5) -> List[str]:
    """Extract the top-N most distinctive keywords from the email body."""
    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=50)
        tfidf_matrix = vectorizer.fit_transform([body])
        scores = tfidf_matrix.toarray()[0]
        feature_names = np.array(vectorizer.get_feature_names_out())
        top_indices = scores.argsort()[::-1][:top_n]
        return [feature_names[i] for i in top_indices if scores[i] > 0]
    except ValueError:
        return []


def compute_priority_score(category: str, body: str, deadlines: List[Dict]) -> float:
    """
    Combine category weight + urgency keyword density + presence of deadlines
    into a single 0-100 priority score.
    """
    base = 50 + CATEGORY_WEIGHT.get(category, 0)

    # Boost if there's a resolvable deadline
    if deadlines:
        base += 10 if any(d["date"] for d in deadlines) else 5

    # Boost slightly per urgent keyword found directly
    lowered = body.lower()
    urgent_hits = sum(1 for kw in CATEGORY_KEYWORDS["Urgent"] if kw in lowered)
    base += urgent_hits * 3

    return float(max(0, min(100, base)))


def maybe_enhance_with_llm(subject: str, body: str, result: Dict) -> Dict:
    """
    Optional enhancement step: if ANTHROPIC_API_KEY or OPENAI_API_KEY is set
    in the environment, ask an LLM to double-check/refine the category and
    produce a sharper summary. Silently no-ops if no key is configured, so
    the platform works fully offline by default.
    """
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        return result  # no key configured — skip enhancement

    try:
        import anthropic  # imported lazily so it's an optional dependency

        client = anthropic.Anthropic(api_key=anthropic_key)
        prompt = (
            "You are an email intelligence assistant. Given this email, "
            "return a JSON object with keys 'category' (one of: Urgent, "
            "Action Needed, Meeting, Informational, Spam-like) and "
            "'summary' (a 1-2 sentence summary).\n\n"
            f"Subject: {subject}\nBody: {body}"
        )
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        # Parsing left intentionally simple — production code should validate
        # this more defensively (e.g. json.loads with try/except + schema check).
        text = response.content[0].text
        import json
        parsed = json.loads(text)
        result["category"] = parsed.get("category", result["category"])
        result["summary"] = parsed.get("summary", result["summary"])
    except Exception:
        # Any failure (no network, bad key, parsing issue) — fall back
        # silently to the rule-based result rather than breaking the request.
        pass

    return result


def process_email(sender: str, subject: str, body: str) -> Dict:
    """
    The main entry point: run the full intelligence pipeline on a raw email
    and return everything the API/database needs.
    """
    category = classify_email(subject, body)
    action_items = extract_action_items(body)
    deadlines = extract_deadlines(body)
    summary = summarize(body)
    keywords = extract_keywords(body)
    priority_score = compute_priority_score(category, body, deadlines)

    result = {
        "category": category,
        "action_items": action_items,
        "deadlines": deadlines,
        "summary": summary,
        "keywords": keywords,
        "priority_score": priority_score,
    }

    result = maybe_enhance_with_llm(subject, body, result)
    return result
