import sqlite3
import json
from datetime import datetime

def insert_session(email, otp_link, client_token, account_age, cookies, headers):
    # Serialize cookies and headers to JSON strings
    cookies_json = json.dumps(cookies)
    headers_json = json.dumps(headers)

    # Connect to SQLite database
    conn = sqlite3.connect('sessions.db')
    cur = conn.cursor()

    # Insert the session data
    cur.execute('''
    INSERT INTO sessions (email, otp_link, client_token, account_age, cookies, headers)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (email, otp_link, client_token, account_age, cookies_json, headers_json))

    # Commit and close the connection
    conn.commit()
    cur.close()
    conn.close()

    return "Session data for {email} inserted successfully."

def get_session(email):
    # Connect to SQLite database
    conn = sqlite3.connect('sessions.db')
    cur = conn.cursor()

    # Retrieve the most recent session data for the given email
    cur.execute('''
    SELECT otp_link, client_token, account_age, cookies, headers, timestamp FROM sessions
    WHERE email = ?
    ORDER BY timestamp DESC
    LIMIT 1
    ''', (email,))

    # Fetch the data
    result = cur.fetchone()

    # Close the connection
    cur.close()
    conn.close()

    # If result is found, return it as a dictionary
    if result:
        otp_link, client_token, account_age, cookies_json, headers_json, timestamp = result
        cookies = json.loads(cookies_json)
        headers = json.loads(headers_json)
        return {
            'email': email,
            'otp_link': otp_link,
            'client_token': client_token,
            'account_age': account_age,
            'cookies': cookies,
            'headers': headers,
            'timestamp': timestamp
        }
    else:
        print(f"No session data found for {email}.")
        return None