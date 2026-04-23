# nlp_model.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
import re
from datetime import date, timedelta
from training_data import training_data

# ---------------------------
# 1️⃣ Configuration
# ---------------------------
CONFIDENCE_THRESHOLD = 0.6

# ---------------------------
# 2️⃣ Text Preprocessing
# ---------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\-/ ]', '', text)  # keep - and /
    return text

# ---------------------------
# 3️⃣ Train Model
# ---------------------------
def train_model(training_data):
    texts = [clean_text(d['text']) for d in training_data]
    labels = [d['intent'] for d in training_data]

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1,3), max_features=5000)),
        ('clf', CalibratedClassifierCV(LogisticRegression(max_iter=1000), cv=3))
    ])

    pipeline.fit(texts, labels)
    return pipeline

# ---------------------------
# 4️⃣ Rule-based Intent Booster
# ---------------------------
def rule_based_intent(text):
    text_lower = text.lower()

    if re.search(r'\b(user|employee|person)\b', text_lower):
        return 'get_user'

    if re.search(r'\b(request|pr|purchase)\b', text_lower):
        return 'get_request'

    if re.search(r'\b(total|sum|amount)\b', text_lower):
        return 'get_total'

    return None

# ---------------------------
# 5️⃣ Entity Extraction
# ---------------------------
def extract_entities(text, intent):
    entities = {}
    text_lower = text.lower()

    # Status
    if 'cancel' in text_lower:
        entities['status'] = 'cancelled'
    elif 'pending' in text_lower:
        entities['status'] = 'pending'
    elif 'complete' in text_lower or 'done' in text_lower:
        entities['status'] = 'completed'

    # Timeframes
    today = date.today()

    if 'today' in text_lower:
        entities['date'] = str(today)
    elif 'this week' in text_lower:
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        entities['start_date'] = str(start)
        entities['end_date'] = str(end)
    elif 'this month' in text_lower:
        start = today.replace(day=1)
        end = (start.replace(month=start.month % 12 + 1, day=1) - timedelta(days=1)) if start.month != 12 else today.replace(day=31)
        entities['start_date'] = str(start)
        entities['end_date'] = str(end)

    # --- Request Number Extraction (robust) ---
    if intent == 'get_request':
        # Match sequences that look like request numbers:
        # 2026D22755, AD-2025/342, NM/HP/765, 12345
        match = re.search(r'(?:request|get|details|get details)?\s*([A-Z0-9\-\/]+)', text, re.IGNORECASE)
        if match:
            entities['request_no'] = match.group(1).strip()

    # User extraction
    if intent == 'get_user':
        match = re.search(r'(?:user|employee)\s+([a-zA-Z ]+)', text)
        if match:
            entities['user_name'] = match.group(1).strip()

    return entities

# ---------------------------
# 6️⃣ NLP Processor
# ---------------------------
class NLPProcessor:
    def __init__(self, training_data):
        self.model = train_model(training_data)

    def predict(self, text):
        rule_intent = rule_based_intent(text)
        cleaned = clean_text(text)

        probs = self.model.predict_proba([cleaned])[0]
        classes = self.model.classes_
        ml_intent = classes[probs.argmax()]
        confidence = max(probs)

        # Hybrid decision
        if rule_intent:
            intent = rule_intent
        elif confidence >= CONFIDENCE_THRESHOLD:
            intent = ml_intent
        else:
            intent = 'fallback'

        entities = extract_entities(text, intent)
        return intent, entities, confidence

# ---------------------------
# 7️⃣ Example Usage
# ---------------------------
if __name__ == '__main__':
    bot = NLPProcessor(training_data)

    queries = [
        'Show pending requests this week',
        'Get user John Doe',
        'Find request 2026-DN/266',
        'Total completed purchases this month'
    ]

    for q in queries:
        intent, entities, conf = bot.predict(q)
        print(f'Query: {q}')
        print(f'Intent: {intent}')
        print(f'Confidence: {conf}')
        print(f'Entities: {entities}\n')