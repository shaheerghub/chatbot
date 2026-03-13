training_data = [
    # Existing examples
    {"text": "get user 5", "intent": "get_user"},
    {"text": "show user 10 details", "intent": "get_user"},
    
    # Total purchases variations
    {"text": "total purchases today", "intent": "total_purchase"},
    {"text": "total purchases this week", "intent": "total_purchase"},
    {"text": "total purchases this month", "intent": "total_purchase"},
    {"text": "total purchases this year", "intent": "total_purchase"},
    {"text": "total purchases 2026-03-09", "intent": "total_purchase"},
    
    # Cancelled purchases variations
    {"text": "cancelled purchases today", "intent": "cancelled_purchase"},
    {"text": "cancelled purchases this week", "intent": "cancelled_purchase"},
    {"text": "cancelled purchases this month", "intent": "cancelled_purchase"},
    {"text": "cancelled purchases this year", "intent": "cancelled_purchase"},
    {"text": "cancelled purchases 2026-03-01", "intent": "cancelled_purchase"},
    
    # Alternative phrasings
    {"text": "how many purchases today", "intent": "total_purchase"},
    {"text": "how many purchases were cancelled this week", "intent": "cancelled_purchase"},
    {"text": "show total purchases this month", "intent": "total_purchase"},
    {"text": "show cancelled purchase counts for this year", "intent": "cancelled_purchase"},
    {"text": "purchases for today", "intent": "total_purchase"},
    {"text": "cancelled purchases 2026-02-28", "intent": "cancelled_purchase"},

    {"text": "get request 23867", "intent": "get_request"},
    {"text": "2026DN266", "intent": "get_request"},
    {"text": "2026DN001", "intent": "get_request"},
    {"text": "2026DN010", "intent": "get_request"},
    {"text": "2026DN100", "intent": "get_request"},
    {"text": "2026DN200", "intent": "get_request"},
    {"text": "show 12345", "intent": "get_request"},
    {"text": "request 98765 info", "intent": "get_request"},
    {"text": "get details for request 555", "intent": "get_request"},
]