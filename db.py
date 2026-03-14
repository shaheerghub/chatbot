# db.py
import mysql.connector
from datetime import date


def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="purchasedb",
        port=3306,
        connection_timeout=5,   # fail quickly if DB not responding
        autocommit=True
    )

def query_user(user_id):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, email FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"name": result[0], "email": result[1]}
    return None

def query_user_by_name(user_name):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    # Add % for partial match
    search_name = f"%{user_name}%"
    cursor.execute("SELECT full_name, email FROM users WHERE full_name LIKE %s", (search_name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"name": result[0], "email": result[1]}
    return None

def total_purchase(entities):
    """
    entities can contain:
    - 'date' -> specific date
    - 'start_date' & 'end_date' -> date range (week/month/year)
    - 'status' -> optional purchase status filter
    """

    query = "SELECT COUNT(*) FROM purchase_request WHERE 1=1"
    params = []

    # Filter by specific date
    if 'date' in entities:
        query += " AND requesting_date = %s"
        params.append(entities['date'])

    # Filter by date range (week/month/year)
    elif 'start_date' in entities and 'end_date' in entities:
        query += " AND requesting_date BETWEEN %s AND %s"
        params.extend([entities['start_date'], entities['end_date']])

    # Filter by status if provided
    if 'status' in entities:
        query += " AND status = %s"
        params.append(entities['status'])

    # Execute query
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute(query, tuple(params))
    result = cursor.fetchone()
    conn.close()

    return result[0] if result and result[0] else 0

def query_request(request_no):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)  # return dict directly
    search_no = f"%{request_no}%"  # wrap with % for partial match
    cursor.execute("""SELECT * FROM purchase_request 
                   left join 
                   purchase_actions on purchase_request.requesting_id=purchase_actions.requesting_id 
                   WHERE purchase_actions.is_current=1 and purchase_request.request_no LIKE %s""", (search_no,))
    result = cursor.fetchone()
    conn.close()
    return result