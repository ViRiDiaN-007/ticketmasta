import requests
import sqlite3
import json
import query_db as db

def build_session_from_db(email):
    # Retrieve the latest session data from the database
    session_data = db.get_session(email)

    if session_data:
        # Create a new requests session
        session = requests.Session()

        # Load cookies into the session
        cookies = session_data['cookies']
        for cookie_name, cookie_value in cookies.items():
            session.cookies.set(cookie_name, cookie_value)

        # Load headers into the session
        headers = session_data['headers']
        session.headers.update(headers)

        # Store the OTP link in a variable
        otp_link = session_data['otp_link']

        print(f"Session for {email} built successfully. OTP link: {otp_link}")
        return session, otp_link
    else:
        return None, None
    
def verify_OTP(session, verify_link, otp):
    payload = {"otp":f"{otp}"}

    resp = session.post(verify_link, json=payload)
    return session, resp.text 
# Example usage
if __name__ == "__main__":
    email = 'viritester@yopmail.com'

    # Build a session from the database and get the OTP link
    session, otp_link = build_session_from_db(email)

    if session:
        # Use the session to make a request
        response = session.get('https://google.com')  # Replace with your actual URL
        print(response.status_code)
        
        # Use the OTP link for any additional processing
        print(f"Retrieved OTP Link: {otp_link}")

        print('trying to validate otp')

        session, resp = verify_OTP(session, otp_link, 444444)
        print(resp)
