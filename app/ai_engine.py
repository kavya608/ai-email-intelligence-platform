import re
from dateutil import parser as date_parser
from datetime import datetime

URGENT_KEYWORDS = ['urgent', 'asap', 'immediately', 'critical', 'emergency']
MEETING_KEYWORDS = ['meeting', 'call', 'schedule', 'calendar', 'invite', 'zoom', 'teams']
ACTION_KEYWORDS = ['please', 'need you to', 'action required', 'complete', 'submit', 'review']
SPAM_KEYWORDS = ['unsubscribe', 'winner', 'free money', 'click here', 'limited offer']

ACTION_PHRASES = [
    'please', 'need you to', 'make sure', 'ensure', 'submit', 'send',
    'complete', 'review', 'provide', 'kindly', 'must', 'should',
    'action required', 'required to'
]


def categorize_email(subject, body):
    text = (subject or '') + ' ' + (body or '')
    text = text.lower()

    if any(keyword in text for keyword in URGENT_KEYWORDS):
        return 'Urgent'
    elif any(keyword in text for keyword in MEETING_KEYWORDS):
        return 'Meeting'
    elif any(keyword in text for keyword in ACTION_KEYWORDS):
        return 'Action Needed'
    elif any(keyword in text for keyword in SPAM_KEYWORDS):
        return 'Spam-like'
    else:
        return 'Informational'


def calculate_priority(category, text, has_deadline):
    base_scores = {
        'Urgent': 80,
        'Action Needed': 60,
        'Meeting': 50,
        'Informational': 20,
        'Spam-like': 5
    }

    score = base_scores.get(category, 20)

    text_lower = text.lower()
    if any(keyword in text_lower for keyword in URGENT_KEYWORDS):
        score += 10

    if has_deadline:
        score += 10

    return min(score, 100)


def extract_action_items(body):
    if not body:
        return []

    sentences = re.split(r'(?<=[.!?])\s+', body)

    action_items = []
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(phrase in sentence_lower for phrase in ACTION_PHRASES):
            action_items.append(sentence.strip())

    return action_items


def extract_deadline(text):
    if not text:
        return None
    pattern = r"\b(?:by|before|due|deadline is|deadline:)\s+([A-Za-z0-9,'\s]+?)(?:[.,!\n]|$)"
    
    matches = re.findall(pattern, text, re.IGNORECASE)

    for match in matches:
        candidate = match.strip()
        try:
            parsed_date = date_parser.parse(candidate, fuzzy=True, default=datetime.now())
            return parsed_date
        except (ValueError, OverflowError):
            continue

    return None

from sklearn.feature_extraction.text import TfidfVectorizer


def split_sentences(text):
    if not text:
        return []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def summarize_email(body, num_sentences=3):
    """
    Picks the num_sentences most 'important' sentences (by TF-IDF score)
    and returns them in their original order.
    """
    sentences = split_sentences(body)

    if len(sentences) <= num_sentences:
        return body

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(sentences)

    sentence_scores = tfidf_matrix.sum(axis=1).A1

    top_indices = sentence_scores.argsort()[-num_sentences:]
    top_indices_sorted = sorted(top_indices)

    summary = ' '.join([sentences[i] for i in top_indices_sorted])
    return summary


def extract_keywords(body, num_keywords=5):
    """
    Returns the most distinctive words in the email, by TF-IDF score,
    treating each sentence as its own mini-document.
    """
    sentences = split_sentences(body)

    if len(sentences) < 2:
        return []

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(sentences)

    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.sum(axis=0).A1

    top_indices = scores.argsort()[-num_keywords:][::-1]
    keywords = [feature_names[i] for i in top_indices]

    return keywords

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv('ANTHROPIC_API_KEY')
client = Anthropic(api_key=api_key) if api_key else None


def is_llm_enabled():
    return client is not None


def enhance_categorization(subject, body, rule_based_category):
    """
    If an Anthropic API key is configured, asks Claude to refine the
    rule-based category. Falls back to the rule-based result if the
    LLM isn't configured, returns something unexpected, or the call
    fails for any reason.
    """
    if not is_llm_enabled():
        return rule_based_category

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=20,
            messages=[{
                "role": "user",
                "content": (
                    "Classify this email into exactly one category: "
                    "Urgent, Action Needed, Meeting, Informational, or Spam-like. "
                    "Reply with only the category name, nothing else.\n\n"
                    f"Subject: {subject}\nBody: {body}"
                )
            }]
        )
        llm_category = message.content[0].text.strip()

        valid_categories = ['Urgent', 'Action Needed', 'Meeting', 'Informational', 'Spam-like']
        if llm_category in valid_categories:
            return llm_category
        return rule_based_category

    except Exception as e:
        print(f"LLM categorization failed, falling back to rule-based: {e}")
        return rule_based_category


def enhance_summary(body, rule_based_summary):
    """
    Same fallback philosophy as above, but for summarization.
    """
    if not is_llm_enabled():
        return rule_based_summary

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=150,
            messages=[{
                "role": "user",
                "content": f"Summarize this email in 1-2 concise sentences:\n\n{body}"
            }]
        )
        return message.content[0].text.strip()

    except Exception as e:
        print(f"LLM summarization failed, falling back to TF-IDF summary: {type(e).__name__}: {e}")
        return rule_based_summary