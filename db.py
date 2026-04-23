# db.py
import mysql.connector
from mysql.connector import pooling

# ---------------------------
# 1️⃣ Connection Pool Setup
# ---------------------------
POOL_NAME = 'mypool'
POOL_SIZE = 10

pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name=POOL_NAME,
    pool_size=POOL_SIZE,
    host='172.16.134.20',
    user='root',
    password='',
    database='purchasedb',
    port=3306,
    autocommit=True
)

# ---------------------------
# 2️⃣ Utility Functions
# ---------------------------
def get_mysql_connection():
    return pool.get_connection()

# ---------------------------
# 3️⃣ User Queries
# ---------------------------
def query_user(user_id):
    try:
        with get_mysql_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT full_name, email FROM users WHERE user_id = %s', (user_id,))
            result = cursor.fetchone()
        return {'name': result[0], 'email': result[1]} if result else None
    except Exception as e:
        print('DB Error:', e)
        return None


def query_user_by_name(user_name):
    try:
        with get_mysql_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            search_name = f'%{user_name}%'
            cursor.execute('SELECT full_name, email FROM users WHERE full_name LIKE %s', (search_name,))
            results = cursor.fetchall()
        return results
    except Exception as e:
        print('DB Error:', e)
        return []


def query_user_by_username(username):
    try:
        with get_mysql_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT user_name as username, password, full_name FROM users WHERE user_name = %s LIMIT 1', (username,))
            user = cursor.fetchone()
        return user
    except Exception as e:
        print('DB Error:', e)
        return None

# ---------------------------
# 4️⃣ Purchase Queries
# ---------------------------
def total_purchase(entities):
    try:
        query = 'SELECT COUNT(*) as total_count, IFNULL(SUM(final_amount),0) as total_amount FROM purchase_request WHERE 1=1'
        params = []

        if 'date' in entities:
            query += ' AND requesting_date = %s'
            params.append(entities['date'])
        elif 'start_date' in entities and 'end_date' in entities:
            query += ' AND requesting_date BETWEEN %s AND %s'
            params.extend([entities['start_date'], entities['end_date']])

        if 'status' in entities:
            query += ' AND status = %s'
            params.append(entities['status'])

        with get_mysql_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, tuple(params))
            result = cursor.fetchone()

        return result if result else {'total_count': 0, 'total_amount': 0}
    except Exception as e:
        print('DB Error:', e)
        return {'total_count': 0, 'total_amount': 0}


def query_request(request_no):
    try:
        with get_mysql_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            search_no = f'%{request_no}%'
            cursor.execute('''
                SELECT * FROM purchase_request 
                LEFT JOIN purchase_actions ON purchase_request.requesting_id = purchase_actions.requesting_id
                WHERE purchase_actions.is_current = 1 AND purchase_request.request_no LIKE %s
            ''', (search_no,))
            result = cursor.fetchone()
        return result
    except Exception as e:
        print('DB Error:', e)
        return None

def cancelled_purchase(entities):
    try:
        query = 'SELECT COUNT(*) as total_count, IFNULL(SUM(final_amount),0) as total_amount ' \
        'FROM purchase_request WHERE cancel=1'
        params = []

        if 'date' in entities:
            query += ' AND cancel_date = %s'
            params.append(entities['date'])
        elif 'start_date' in entities and 'end_date' in entities:
            query += ' AND cancel_date BETWEEN %s AND %s'
            params.extend([entities['start_date'], entities['end_date']])


        with get_mysql_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, tuple(params))
            result = cursor.fetchone()

        return result if result else {'total_count': 0, 'total_amount': 0}
    except Exception as e:
        print('DB Error:', e)
        return {'total_count': 0, 'total_amount': 0}
