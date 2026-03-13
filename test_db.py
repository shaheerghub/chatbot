# test_db.py
import mysql.connector

try:
    conn = mysql.connector.connect(
        host="172.16.134.20",
        user="ariesuser1",
        password="hj67#bfgd",
        database="purchasedb",
        connection_timeout=5  # <-- don't wait too long
    )
    print("Connected!")
    conn.close()
except Exception as e:
    print("DB connection error:", e)