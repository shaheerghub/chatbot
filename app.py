# app.py

from flask import Flask, render_template, request, jsonify
from db import query_user, total_purchase, query_user_by_name, query_request
from nlp_model import predict_intent

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    intent, entities = predict_intent(user_input)  # <-- entities is a dict now

    if intent == "get_user":
        user_name = entities.get("user_name")
        user = query_user_by_name(user_name)
        response = f"User: {user['name']}, Email: {user['email']}" if user else "User not found"

    elif intent == "total_purchase":
        # Pass the entire entities dict to the function
        purchases = total_purchase(entities)
        # For display: show which timeframe/date
        display_date = entities.get("date") or entities.get("timeframe", "unknown period")
        response = f"Total purchases for {display_date}: {purchases}"

    elif intent == "get_request":
        request_no = entities.get("request_no")
        status_map = {
            "C": "Complete",
            "AP": "Approved",
            "NC": "Need Clarification",
            "V": "Verified",
            "SA": "Send for Approval"
        }
        req = query_request(request_no)
        if req:
            # Format the response nicely
            currency = req.get('final_amount_currency')
            status_text = status_map.get(req.get('status'), req.get('status'))
            response = (
                f"""
        <table style="border-collapse: collapse; width: 100%; max-width: 520px; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.08);">
    <tr style="background: linear-gradient(135deg, #1a1d27, #2a2f45);">
        <th style="padding: 12px 16px; text-align: left; color: #a0aec0; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; width: 40%;">Field</th>
        <th style="padding: 12px 16px; text-align: left; color: #a0aec0; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em;">Value</th>
    </tr>
    <tr style="background-color: #ffffff;">
        <td style="padding: 11px 16px; color: #6b7280; font-weight: 500; border-bottom: 1px solid #f0f0f0;">Request No</td>
        <td style="padding: 11px 16px; color: #111827; font-weight: 600; border-bottom: 1px solid #f0f0f0;">{req['request_no']}</td>
    </tr>
    <tr style="background-color: #fafafa;">
        <td style="padding: 11px 16px; color: #6b7280; font-weight: 500; border-bottom: 1px solid #f0f0f0;">Requested On</td>
        <td style="padding: 11px 16px; color: #111827; font-weight: 600; border-bottom: 1px solid #f0f0f0;">{req['requesting_date']}</td>
    </tr>
    <tr style="background-color: #ffffff;">
        <td style="padding: 11px 16px; color: #6b7280; font-weight: 500; border-bottom: 1px solid #f0f0f0;">Total Amount</td>
        <td style="padding: 11px 16px; color: #111827; font-weight: 700; border-bottom: 1px solid #f0f0f0;">{req.get('final_amount', '0')} {currency}</td>
    </tr>
    <tr style="background-color: #fafafa;">
        <td style="padding: 11px 16px; color: #6b7280; font-weight: 500;">Status</td>
        <td style="padding: 11px 16px;">
            <span style="display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; background-color: #ecfdf5; color: #059669; border: 1px solid #a7f3d0;">
                {req['action_id'].replace('_', ' ').title()} {status_text}
            </span>
        </td>
    </tr>
</table>
        """
            )
        else:
            response = f"No request found with number {request_no}"

    else:
        response = "I didn't understand that."

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)