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

    if any(keyword in text for keyword in SPAM_KEYWORDS):
        return 'Spam-like'

    elif any(keyword in text for keyword in URGENT_KEYWORDS):
        return 'Urgent'

    elif any(keyword in text for keyword in MEETING_KEYWORDS):
        return 'Meeting'

    elif any(keyword in text for keyword in ACTION_KEYWORDS):
        return 'Action Needed'

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

    if category == 'Spam-like':
        return score

    text_lower = text.lower()

    if any(keyword in text_lower for keyword in URGENT_KEYWORDS):
        score += 10

    if has_deadline:
        score += 10

    return min(score, 100)

def extract_action_items(body):
    if not body:
        return []

    sentences = re.split(r'(?<!Rs)(?<!Mrs)(?<!Mr)(?<=[.!?])\s+', body)
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

    abbreviations = [
        "Rs.",
        "Mr.",
        "Mrs.",
        "Dr.",
        "Ms.",
        "Inc.",
        "Ltd."
    ]

    for abbr in abbreviations:
        text = text.replace(abbr, abbr.replace(".", "<DOT>"))

    sentences = re.split(r'(?<=[.!?])\s+', text)

    sentences = [
        s.replace("<DOT>", ".").strip()
        for s in sentences
        if s.strip()
    ]

    return sentences


def summarize_email(body, num_sentences=1):
    sentences = split_sentences(body)

    if len(sentences) <= 2:
        return sentences[0]

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(sentences)

    sentence_scores = tfidf_matrix.sum(axis=1).A1

    top_indices = sentence_scores.argsort()[-num_sentences:]
    top_indices_sorted = sorted(top_indices)

    summary = ' '.join([sentences[i] for i in top_indices_sorted])
    return summary


def extract_keywords(body, num_keywords=5):

    if not body:
        return []

    if len(split_sentences(body)) < 2:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([body])

    else:
        sentences = split_sentences(body)
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(sentences)

    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.sum(axis=0).A1

    top_indices = scores.argsort()[-num_keywords:][::-1]

    return [feature_names[i] for i in top_indices]

import spacy

nlp = spacy.load("en_core_web_sm")

ENTITY_MAPPING = {
    "PERSON": "people",
    "ORG": "organizations",
    "DATE": "dates",
    "MONEY": "money",
    "GPE": "locations",
}

def extract_named_entities(text):

    result = {
        "people": [],
        "organizations": [],
        "dates": [],
        "money": [],
        "locations": []
    }

    if not text:
        return result

    doc = nlp(text)

    for ent in doc.ents:

        key = ENTITY_MAPPING.get(ent.label_)

        if key:
            value = ent.text.strip()

            if key == "organizations" and value.lower().startswith("the "):
                value = value[4:]

            if value not in result[key]:
                result[key].append(value)

    # Regex-based extraction for Indian currency
    money_pattern = r'(?:₹|Rs\.?|INR|\?)\s?\d+(?:,\d+)*(?:\.\d+)?'

    regex_money = re.findall(money_pattern, text, flags=re.IGNORECASE)

    for amount in regex_money:
        if amount not in result["money"]:
            result["money"].append(amount)

    cleaned_orgs = []

    for org in result["organizations"]:

        if re.search(r"\d", org):
            continue

        if len(org.split()) > 3:
            continue

        if org not in cleaned_orgs:
            cleaned_orgs.append(org)

    result["organizations"] = cleaned_orgs

    return result
