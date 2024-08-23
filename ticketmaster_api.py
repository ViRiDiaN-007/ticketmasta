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
from requests.structures import CaseInsensitiveDict

def gen_code_verifier():
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
    return re.sub('[^a-zA-Z0-9]+', '', code_verifier)

def gen_code_challenge(code_verifier):
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
    return code_challenge.replace('=', '')

def gen_device_id(length=56):
    characters = string.ascii_letters + string.digits
    device_id = ''.join(random.choice(characters) for _ in range(length))
    return device_id

def gen_state(length=16):
    characters = string.ascii_letters + string.digits
    state = ''.join(random.choice(characters) for _ in range(length))
    return state

def gen_time():
    return int(time.time() * 1000)

def gen_px2():
    uuid1 = uuid.uuid4()
    uuid2 = uuid.uuid4()
    timestamp = int(time.time())
    _timestamp = str(timestamp).encode()
    val = f"{uuid1}:{uuid2}:{_timestamp}".encode()
    hash_object = hashlib.sha256(val)
    px_hash = hash_object.hexdigest()

    cookie_json = json.dumps({"u":f"{uuid1}","v":f"{uuid2}","t":timestamp,"h":f"{px_hash}"})
    return base64.b64encode(cookie_json.encode()).decode()


def gen_login_url():
    #code_challenge = gen_code_challenge(code_verifier)
    #state = gen_state()
    device_id = gen_device_id()
    return f'https://auth.ticketmaster.com/as/authorization.oauth2?client_id=8bf7204a7e97.web.ticketmaster.us&response_type=code'\
            '&scope=openid+profile+phone+email+tm&redirect_uri=https%3A%2F%2Fidentity.ticketmaster.com%2Fexchange&visualPresets=tm'\
            f'&lang=en-us&placementId=mytmlogin&hideLeftPanel=false&integratorId=prd1741.iccp&intSiteToken=tm-us&deviceId={device_id}'

def post_login(email, password,_px2, login_url ):
    
    session = requests.Session()
    session.proxies = {
            'http': 'http://viridian007:FctXDTqOR43hyn7y_country-UnitedStates@proxy.packetstream.io:31112',
            'https': 'http://viridian007:FctXDTqOR43hyn7y_country-UnitedStates@proxy.packetstream.io:31112'
        }
    headers = { "Host": "auth.ticketmaster.com",
                "tm-oauth-type": "tm-auth",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
                "tm-site-token": "tm-ca",
                "tm-placement-id": "hostOnlyLogin",
                "Origin": "https://auth.ticketmaster.com",
                "tm-integrator-id": "prd300.psdk",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Site": "same-origin",
                "nds-pmd": "",
                "Connection": "keep-alive",
                "tm-client-id": "8bf7204a7e97.web.ticketmaster.us",
                "Accept-Language": "en-ca",
                "Accept": "*/*",
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip, deflate, br",
                "Sec-Fetch-Mode": "cors"}
    r = session.get(login_url, headers=headers)
    payload = {"email":f"{email}","password":f"{password}","rememberMe":False,"externalUserToken":None,"siteToken":"tm-ca"}
    cookies = {'_px2': f'{_px2}'}
    headers = { "Host": "auth.ticketmaster.com",
                "tm-oauth-type": "tm-auth",
                "Referer": f"{login_url}",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
                "tm-site-token": "tm-ca",
                "tm-placement-id": "hostOnlyLogin",
                "Origin": "https://auth.ticketmaster.com",
                "tm-integrator-id": "prd300.psdk",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Site": "same-origin",
                "nds-pmd": "",
                "Connection": "keep-alive",
                "tm-client-id": "8bf7204a7e97.web.ticketmaster.us",
                "Accept-Language": "en-ca",
                "Accept": "*/*",
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip, deflate, br",
                "Sec-Fetch-Mode": "cors"}
                
    resp = session.post('https://auth.ticketmaster.com/json/sign-in', headers=headers, cookies=cookies, json=payload,allow_redirects=False)
    #print(resp.text)
    return session, resp.text

def parse_code(resp):
    print(resp)
    return json.loads(resp)['_links']['continueLink']['source'].split('code=')[1].split('&')[0]

def exchange_link(session, exchange_link):
    session.headers.update({ "Host": "identity.ticketmaster.com",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
                            "Accept-Language": "en-US,en;q=0.5",
                            "Accept-Encoding": "gzip, deflate, br, zstd",
                            "Connection": "keep-alive",
                            "Referer": "https://auth.ticketmaster.com/",
                            "Upgrade-Insecure-Requests": "1",
                            "Sec-Fetch-Dest": "document",
                            "Sec-Fetch-Mode": "navigate",
                            "Sec-Fetch-Site": "same-site",
                            "Sec-Fetch-User": "?1",
                            "Priority": "u=0, i",
                            "TE": "trailers"})

    resp = session.get(exchange_link,allow_redirects=False)
    print(resp.status_code)
    return session, resp.text

def generate_device_string():
    mask = "?u?u?u?u?u?u?u?u-?u?u?u?u-4?u?u?u-?u?u?u?u-?u?u?u?u?u?u?u?u?u?u?u?u"
    result = []
    pattern = string.ascii_uppercase
    for char in mask:
        if char == '?u':
            result.append(random.choice(pattern))
        else:
            result.append(char)
    return ''.join(result)

def client_token(session):
    url = 'https://my.ticketmaster.com/account/mfa/json/client-token'
    session.headers.update({"Host": "my.ticketmaster.com",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
                            "Accept": "*/*",
                            "Accept-Language": "en-US,en;q=0.5",
                            "Accept-Encoding": "gzip, deflate, br, zstd",
                            "DNT": "1",
                            "Sec-GPC": "1",
                            "Connection": "keep-alive",
                            "Referer": "https://my.ticketmaster.com/settings",
                            #"Cookie": f"_px2=eyJ1IjoiMjhkNDZlYzAtNWFmNi0xMWVmLWIyYzUtM2Y3MjhiOTEzNjhhIiwidiI6IjAzZmExNTZiLTVhZjYtMTFlZi1iMzk3LWQ2M2JkODQ0NDIxZiIsInQiOjE3MjM3MjAxNzk4MjYsImgiOiIxNmIxY2MzNTFjYjQ0MzAwYTA1NzVmYmEwMDI3NmMwZTdlOGQ2YmRhNTRlYmU1N2ZjZDUyM2NkMTRkODRhODQ1In0=; OptanonAlertBoxClosed=2024-08-15T11:03:36.468Z; SOTC={access_token}; SORTC=; id-token={id_token}",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",
                            "Priority": "u=0",
                            "TE": "trailers",})
    print('client token resp')
    for num in range(15):
        resp = session.get(url)
        if not str(resp.status_code).startswith('4') and resp.text != '{"response":"block"}':
            break
    print(resp)
    return session, resp.text

def get_OTP_link(session, client_token, login_link):
    
    session.proxies = {
            'http': 'http://viridian007:FctXDTqOR43hyn7y_country-UnitedStates@proxy.packetstream.io:31112',
            'https': 'http://viridian007:FctXDTqOR43hyn7y_country-UnitedStates@proxy.packetstream.io:31112'
        }
    session.headers.update({"Host": "identity.ticketmaster.com",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
                            "Accept": "*/*",
                            "Accept-Language": "en-us",
                            "Accept-Encoding": "gzip, deflate, br",
                            "tm-site-token": "tm-us",
                            "tm-client-id": "790d0a160782.prd212.myAccount",
                            "integrator-host": "https://my.ticketmaster.com",
                            "Connection": "keep-alive",
                            "Referer": f"{login_link}",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",})
    
    url = f'https://identity.ticketmaster.com/mfa/json/device/verification/init?clientId=790d0a160782.prd212.myAccount&clientToken={client_token}'
    for num in range(15):
        resp = session.get(url)
        if str(resp.status_code).startswith('2') or str(resp.status_code).startswith('3') and resp.text != '{"response":"block"}':
            break
    return session, resp.text

def send_OTP(session, link):
    '''session.proxies = {
            'http': 'http://viridian007:FctXDTqOR43hyn7y_country-UnitedStates@proxy.packetstream.io:31112',
            'https': 'http://viridian007:FctXDTqOR43hyn7y_country-UnitedStates@proxy.packetstream.io:31112'
        }'''
    for num in range(15):
        resp = session.post(link)
        if str(resp.status_code).startswith('2') or str(resp.status_code).startswith('3')and resp.text != '{"response":"block"}':
            break
    return session, resp.text

def verify_OTP(session, verify_link, otp):
    payload = {"otp":f"{otp}"}
    '''session.proxies = {
            'http': 'http://viridian007:FctXDTqOR43hyn7y_country-UnitedStates@proxy.packetstream.io:31112',
            'https': 'http://viridian007:FctXDTqOR43hyn7y_country-UnitedStates@proxy.packetstream.io:31112'
        }'''
    for num in range(15):
        resp = session.post(verify_link, json=payload)
        print('verify otp response')
        print(resp.text)
        if str(resp.status_code).startswith('2') or str(resp.status_code).startswith('3')and resp.text != '{"response":"block"}':
            break
    return session, resp.text 

def capture_info(session):
    resp = session.get('https://my.ticketmaster.com/user-account/json/profile')
    return session, resp.text

def save_device(session, client_token, otp_token):
    session.headers.update({"Host": "identity.ticketmaster.com",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
                            "Accept": "*/*",
                            "Accept-Language": "en-us",
                            "Accept-Encoding": "gzip, deflate, br",
                            "tm-site-token": "tm-us",
                            "tm-client-id": "790d0a160782.prd212.myAccount",
                            "integrator-host": "https://my.ticketmaster.com",
                            "Connection": "keep-alive",
                            #"Referer": f"https://identity.ticketmaster.com/mfa/widget.html?clientId=790d0a160782.prd212.myAccount&clientToken={client_token}&lang=en-us",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",})
    url = f'https://identity.ticketmaster.com/mfa/json/device/save?clientId=790d0a160782.prd212.myAccount&clientToken={client_token}&deliveryOption=EMAIL'
    payload = {"verifiedOtpToken":f"{otp_token}"}
    for num in range(10):
        resp = session.post(url, json = payload)
        if str(resp.status_code).startswith('2') or str(resp.status_code).startswith('3')and resp.text != '{"response":"block"}':
            break
    return session, resp.text

def update_email(session, email, verified_device_token):
    url = "https://my.ticketmaster.com/account/json/email"

    session.headers.update( {"Host": "my.ticketmaster.com",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
                            "Accept": "*/*",
                            "Accept-Language": "en-us",
                            "Accept-Encoding": "gzip, deflate, br",
                            "tm-site-token": "tm-us",
                            "tm-client-id": "790d0a160782.prd212.myAccount",
                            "integrator-host": "https://my.ticketmaster.com",
                            "Connection": "keep-alive",
                            "Referer": f"https://my.ticketmaster.com/settings",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin"})
    session.cookies.set('ma.dvt', verified_device_token)
    payload = {"newEmail":f"{email}"}
    '''cookies = {"ma.dvt":verified_device_token,
               "id-token":id_token,
               "SOTC":access_token,
               }'''

    for num in range(15):
        resp = session.post(url, json=payload)
        if str(resp.status_code).startswith('2') or str(resp.status_code).startswith('3')and resp.text != '{"response":"block"}':
            break

    print(resp.status_code)
    return session, resp.text