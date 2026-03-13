# nlp_model.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from training_data import training_data
import re
from datetime import date, timedelta, datetime

# ---------------------------
# 1️⃣ Preprocess Training Data
# ---------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9 ]', '', text)   # remove punctuation
    text = re.sub(r'\d+', 'number', text)    # replace numbers with 'number' token
    return text

texts = [clean_text(d['text']) for d in training_data]
labels = [d['intent'] for d in training_data]

# ---------------------------
# 2️⃣ Vectorizer & Classifier
# ---------------------------
vectorizer = TfidfVectorizer(ngram_range=(1,2), stop_words='english', max_features=3000)
X = vectorizer.fit_transform(texts)

clf = LogisticRegression(max_iter=1000, solver='lbfgs')
clf.fit(X, labels)

# ---------------------------
# 3️⃣ Entity Extraction
# ---------------------------
def extract_entities(text, intent):
    entities = {}
    text_lower = text.lower()

    # --- Status ---
    if "cancelled" in text_lower or "canceled" in text_lower:
        entities['status'] = "cancelled"
    elif "pending" in text_lower:
        entities['status'] = "pending"
    elif "completed" in text_lower or "done" in text_lower:
        entities['status'] = "completed"

    # --- Timeframe ---
    today = date.today()
    if "today" in text_lower:
        entities['timeframe'] = "today"
        entities['date'] = str(today)
    elif "this week" in text_lower:
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        entities['timeframe'] = "this_week"
        entities['start_date'] = str(start_week)
        entities['end_date'] = str(end_week)
    elif "this month" in text_lower:
        start_month = today.replace(day=1)
        end_month = (start_month.replace(month=start_month.month % 12 + 1, day=1) - timedelta(days=1)) \
                    if start_month.month != 12 else today.replace(day=31)
        entities['timeframe'] = "this_month"
        entities['start_date'] = str(start_month)
        entities['end_date'] = str(end_month)
    elif "this year" in text_lower:
        start_year = today.replace(month=1, day=1)
        end_year = today.replace(month=12, day=31)
        entities['timeframe'] = "this_year"
        entities['start_date'] = str(start_year)
        entities['end_date'] = str(end_year)

    # --- Specific date (YYYY-MM-DD) ---
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
    if date_match:
        entities['date'] = date_match.group(1)

    # --- User Extraction ---
    if intent == 'get_user':
        match = re.search(r'get user (.+)', text, re.IGNORECASE)
        if match:
            entities['user_name'] = match.group(1).strip()

    # --- Request Number Extraction ---
    if intent == 'get_request':
        match = re.search(r'(?:request|get)?\s*([\w\-/]+)', text, re.IGNORECASE)
        if match:
            entities['request_no'] = match.group(1).strip()

    # --- Numbers in general (like PR number or quantity) ---
    numbers = re.findall(r'\d+', text)
    if numbers:
        entities['numbers'] = numbers

    return entities

# ---------------------------
# 4️⃣ Predict Intent
# ---------------------------
def predict_intent(text):
    text_clean = clean_text(text)
    intent = clf.predict(vectorizer.transform([text_clean]))[0]
    entities = extract_entities(text, intent)
    return intent, entities

# ---------------------------
# Example Usage
# ---------------------------
if __name__ == "__main__":
    queries = [
        "Show total purchases today",
        "Get user John Doe",
        "Pending PRs this week",
        "Get request 2026-DN/266",
        "Completed requests this month"
    ]

    for q in queries:
        intent, entities = predict_intent(q)
        print(f"Query: {q}")
        print(f"Intent: {intent}")
        print(f"Entities: {entities}\n")