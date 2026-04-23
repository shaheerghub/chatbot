# app.py

import os
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import check_password_hash
import bcrypt
from db import query_user, total_purchase, cancelled_purchase, query_user_by_name, query_request, query_user_by_username
from nlp_model import NLPProcessor
from training_data import training_data

# ---------------------------
# Flask App Setup
# ---------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
app.config.update({
    'SESSION_COOKIE_SAMESITE': 'Lax',
    'SESSION_COOKIE_SECURE': False,
    'SESSION_COOKIE_HTTPONLY': True,
})

CORS(app, supports_credentials=True, resources={r"/*": {"origins": [
    "http://localhost",
    "http://localhost:5000",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080"
]}})

# ---------------------------
# Initialize NLP Processor
# ---------------------------
bot = NLPProcessor(training_data)

# ---------------------------
# Routes
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/auth/status')
def auth_status():
    return jsonify({
        'authenticated': bool(session.get('username')),
        'username': session.get('username')
    })

@app.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.json or {}
    username = (data.get('username') or data.get('user_name') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required.'}), 400

    user = query_user_by_username(username)
    if not user:
        return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401

    stored_hash = user.get('password_hash') or user.get('password') or ''
    if not stored_hash:
        return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401

    if stored_hash.startswith(('$2y$', '$2b$', '$2a$')):
        try:
            if not bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid password hash format.'}), 500
    else:
        if not check_password_hash(stored_hash, password):
            return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401

    session['username'] = username
    session['full_name'] = user.get('full_name')
    return jsonify({'success': True, 'message': 'Authentication successful.'})

# ---------------------------
# Chat Routes
# ---------------------------
@app.route('/chat', methods=['POST','OPTIONS'])
def chat_root():
    return chat_module('purchase')

@app.route("/<module>/chat", methods=["POST","OPTIONS"])
def chat_module(module):
    if request.method == "OPTIONS":
        return "", 200

    if not session.get('username'):
        return jsonify({'error': 'auth_required', 'message': 'Authentication required.'}), 401

    data = request.json or {}
    user_input = data.get("message", "")

    # --- NLP Prediction ---
    intent, entities, confidence = bot.predict(user_input)
    
    # --- Response Handling ---
    if module == "purchase":
        if intent == "get_user":
            user_name = entities.get("user_name")
            users = query_user_by_name(user_name)
            if users:
                user = users[0]  # take first match
                response = f"User: {user['full_name']}, Email: {user['email']}"
            else:
                response = "User not found"

        elif intent == "get_total" or intent == "total_purchase":
            purchases = total_purchase(entities)
            display_date = entities.get("date") or entities.get("timeframe", "unknown period")
            response = f"Total purchases for {display_date}: Count={purchases.get('total_count',0)}, Amount={purchases.get('total_amount',0)}"

        elif intent == "cancelled_purchase":
            cancelled_purchases = cancelled_purchase(entities)
            display_date = entities.get("date") or entities.get("timeframe", "unknown period")
            response = f"Total purchases cancelled on {display_date}: Count={cancelled_purchases.get('total_count',0)}, Amount={cancelled_purchases.get('total_amount',0)}"

        elif intent == "get_request":
            request_no = entities.get("request_no")
            status_map = {"C": "Complete", "AP": "Approved", "NC": "Need Clarification", "V": "Verified", "SA": "Send for Approval", "AC": "Approved with CC"}
            req = query_request(request_no)
            if req:
                currency = req.get('final_amount_currency') or 'AED'
                status_text = status_map.get(req.get('status'), req.get('status', 'Unknown'))
                status_display = f"{req.get('action_id','').replace('_',' ').title()} {status_text}"
                table_data = {
                    "type": "table",
                    "title": f"Purchase Request #{req['request_no']}",
                    "columns": [
                        {"label": "Field", "key": "field"},
                        {"label": "Value", "key": "value"}
                    ],
                    "rows": [
                        {"field": "Request No", "value": req['request_no']},
                        {"field": "Requested On", "value": req['requesting_date']},
                        {"field": "Total Amount", "value": f"{req.get('final_amount',0)} {currency}"},
                        {"field": "Status", "value": status_display}
                    ]
                }
                response = table_data
            else:
                response = f"No request found with number {request_no}"

        else:
            response = "I didn't understand that."

        return jsonify({"response": response})
    else:
        response = f"Access Denied!"
        return jsonify({"response": response})

# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
