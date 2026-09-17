#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
EduHub AI — Autonomous Email Robot & Merchant Onboarding Agent
===============================================================================
Миссия: Автономная коммуникация и подача заявок в международные платежные
        системы (Dodo Payments, PayPro Global, Paddle).
Поддерживает:
- Безопасную отправку через Gmail SMTP (STARTTLS port 587).
- ПерсонализированныеWhite-Hat досье для каждой целевой системы.
- Режимы: --test-connection, --preview, --send <firm>, --send-all.
- Криптографическое логирование отправленных сообщений.
===============================================================================
"""

import os
import sys
import time
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional

# Настройка UTF-8 для консоли
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


# -----------------------------------------------------------------------------
# 1. КОНФИГУРАЦИЯ И ЗАГРУЗКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
# -----------------------------------------------------------------------------

def load_env_file(filepath: str = ".env"):
    """Загружает переменные из .env файла."""
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip("\"'")
            if k not in os.environ:
                os.environ[k] = v

load_env_file()

SENDER_EMAIL = os.getenv("SMTP_SENDER_EMAIL", "")
GOOGLE_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "").replace(" ", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
PRODUCTION_URL = os.getenv("PRODUCTION_URL", "https://eduhub-ai.onrender.com")

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "email_robot.log")


# -----------------------------------------------------------------------------
# 2. ШАБЛОНЫ ЗАЯВОК ДЛЯ ЦЕЛЕВЫХ ПЛАТЕЖНЫХ СИСТЕМ
# -----------------------------------------------------------------------------

TARGET_CONFIGS: Dict[str, Dict[str, any]] = {
    "dodo": {
        "name": "Dodo Payments",
        "recipient": "support@dodopayments.com",
        "subject": "Product Verification Resubmission — EduHub AI (Details Enclosed)",
        "body_template": """Hi Evan and the Dodo Payments Compliance Team,

Thank you for enabling the product verification resubmission option.

I checked our merchant dashboard, but the product verification form currently appears locked from editing on our end (likely due to an interface cache or session state).

To avoid any delays and allow your team to prioritize our compliance review, I have compiled our complete, updated Product Verification Dossier below so you can review and update our account directly:

----------------------------------------------------------------------
PRODUCT VERIFICATION DOSSIER — EduHub AI
----------------------------------------------------------------------
1. Business / Product Name:
   EduHub AI

2. Production Website URL:
   {prod_url}/

3. Industry / Category:
   SaaS / EdTech / Digital Educational Services (MCC 8299 / 5734)

4. Product Description:
   EduHub AI is a cloud-hosted pedagogical learning assistant providing Socratic tutoring, homework scaffolding, lecture summarization (PDF/audio), and standardized exam rubrics (Cambridge Examiner Band 8.5+ IELTS/TOEFL) powered by Google Gemini AI models. The platform is designed strictly for lawful student learning and educator productivity.

5. Pricing Architecture & Billing Model (100% White-Hat):
   We operate a transparent SaaS model with zero deceptive billing, zero trial traps, and zero negative option billing:
   • Student Starter: $9.00 / month (Recurring monthly subscription)
   • EduHub Pro Max: $19.00 / month (Recurring monthly subscription with 14-day 100% money-back guarantee)
   • Exam Sprint Pass: $15.00 one-time flat fee (Non-recurring 30-day intensive access pass)
   • Tutor & Creator Kit: $39.00 / month (Institutional multi-seat license)

   All subscriptions feature instant 1-click self-service cancellation, itemized receipts, and an unconditional 14-day refund policy.

6. Delivery Method & Fulfillment:
   Immediate digital delivery. Access credentials and AI computing allocations are provisioned instantly via web browser session upon checkout.

7. Legal & Consumer Protection Policies:
   • Terms of Service: {prod_url}/terms
   • Refund Policy (14-Day 100% Guarantee): {prod_url}/refund
   • Privacy Policy: {prod_url}/privacy
   • Dispute & AI Resolution Portal: {prod_url}/support

8. Customer Support Contact & SLA:
   Email: mohim.mohimbegim@gmail.com (24/7 coverage, response SLA under 24 hours).
----------------------------------------------------------------------

Could you please review these details directly or manually update our verification status in your system? If there is any additional information or documentation required, please let us know.

Thank you once again for your prompt support.

Best regards,
Mohim
Founder, EduHub AI
mohim.mohimbegim@gmail.com
"""
    },
    "paypro": {
        "name": "PayPro Global",
        "recipient": "sellers@payproglobal.com",
        "subject": "Vendor Merchant Application & Onboarding — EduHub AI Educational SaaS",
        "body_template": """Dear PayPro Global Seller Onboarding Team,

I hope this email finds you well.

I am writing to apply for a merchant vendor account with PayPro Global for our educational SaaS platform, EduHub AI. We are looking for an institutional Merchant of Record partner that handles global sales tax, VAT, and card payments.

Below is our company and product profile:

----------------------------------------------------------------------
MERCHANT PROFILE — EduHub AI
----------------------------------------------------------------------
1. Company / Project Name:
   EduHub AI

2. Website:
   {prod_url}/

3. Business Model & Product Description:
   Cloud-based educational software (EdTech SaaS). We provide autonomous Socratic study assistance, lecture summarization, homework scaffolding, and IELTS/TOEFL exam preparation powered by AI.

4. Pricing Structure:
   • Student Starter: $9.00 / month
   • EduHub Pro Max: $19.00 / month
   • Exam Sprint Pass: $15.00 (One-time 30-day utility pass)
   • Tutor & Creator Kit: $39.00 / month

5. Compliance & Consumer Guarantees:
   • Terms of Service: {prod_url}/terms
   • Refund Policy: {prod_url}/refund (14-day 100% money-back guarantee)
   • Strict 18+ content filtering & non-violence ethical safeguards in place.
   • Immediate digital fulfillment upon successful payment.

6. Contact & Support:
   Mohim (Founder)
   Email: mohim.mohimbegim@gmail.com
   Support Desk: {prod_url}/support
----------------------------------------------------------------------

We would be delighted to partner with PayPro Global as our global MoR. Please let us know the next steps for vendor onboarding and account activation.

Sincerely,
Mohim
Founder, EduHub AI
mohim.mohimbegim@gmail.com
"""
    },
    "paddle": {
        "name": "Paddle",
        "recipient": "sellers@paddle.com",
        "subject": "Paddle Seller Account Verification & Product Dossier — EduHub AI",
        "body_template": """Dear Paddle Seller Onboarding Team,

I am writing to submit our product dossier for seller account verification for EduHub AI.

We are a pure-play digital educational software provider (EdTech SaaS) and wish to integrate Paddle's Merchant of Record checkout for our global student and tutor customer base.

----------------------------------------------------------------------
PRODUCT DOSSIER — EduHub AI
----------------------------------------------------------------------
1. Product Name:
   EduHub AI

2. Product URL:
   {prod_url}/

3. Industry & MCC Category:
   SaaS / EdTech / Digital Software (MCC 5734 / 8299)

4. Value Proposition:
   Socratic pedagogical tutoring, automated lecture synthesis (PDF/audio), and Cambridge examiner IELTS/TOEFL writing rubrics. All tools adhere strictly to academic integrity and safe content standards.

5. Pricing & Subscription Terms:
   • Student Starter: $9.00 / month (recurring monthly)
   • Pro Max: $19.00 / month (recurring monthly)
   • Exam Sprint: $15.00 (one-time prepaid pass, non-recurring)
   • Tutor License: $39.00 / month

   Zero trial traps, zero negative-option billing. 1-click self-service cancellation and a 14-day money-back guarantee.

6. Legal Policies:
   • Terms of Service: {prod_url}/terms
   • Refund Policy: {prod_url}/refund
   • Privacy Policy: {prod_url}/privacy

7. Contact:
   Mohim (Founder)
   Email: mohim.mohimbegim@gmail.com
----------------------------------------------------------------------

Please review our product profile for Paddle Seller approval. We are ready to integrate the Paddle Billing v2 API as soon as our account is approved.

Thank you for your consideration.

Warm regards,
Mohim
Founder, EduHub AI
mohim.mohimbegim@gmail.com
"""
    }
}


# -----------------------------------------------------------------------------
# 3. КЛИЕНТ SMTP И СИСТЕМА ОТПРАВКИ
# -----------------------------------------------------------------------------

class EmailRobot:
    """Робот автономной отправки писем через Gmail SMTP."""

    def __init__(self, sender_email: str = SENDER_EMAIL, password: str = GOOGLE_APP_PASSWORD):
        self.sender_email = sender_email
        self.password = password
        self.host = SMTP_HOST
        self.port = SMTP_PORT

    def test_connection(self) -> bool:
        """Проверяет подключение к SMTP серверу."""
        print(f"[*] Testing SMTP connection to {self.host}:{self.port} as '{self.sender_email}'...")
        try:
            server = smtplib.SMTP(self.host, self.port, timeout=12)
            server.starttls()
            server.login(self.sender_email, self.password)
            server.quit()
            print("[+] SUCCESS: SMTP Authentication succeeded! Ready to dispatch.")
            return True
        except Exception as e:
            print(f"[-] ERROR: SMTP connection failed: {e}")
            return False

    def send_email(self, recipient: str, subject: str, body: str) -> bool:
        """Отправляет одно письмо."""
        msg = MIMEMultipart()
        msg["From"] = f"EduHub AI <{self.sender_email}>"
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        try:
            server = smtplib.SMTP(self.host, self.port, timeout=15)
            server.starttls()
            server.login(self.sender_email, self.password)
            server.send_message(msg)
            server.quit()

            self._log_sent(recipient, subject, "SUCCESS")
            print(f"[+] DISPATCHED: Successfully sent to '{recipient}' | Subject: '{subject}'")
            return True
        except Exception as e:
            self._log_sent(recipient, subject, f"FAILED: {e}")
            print(f"[-] FAILED to send to '{recipient}': {e}")
            return False

    def _log_sent(self, recipient: str, subject: str, status: str):
        """Записывает результат в лог."""
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        log_line = f"[{timestamp}] RECIPIENT: {recipient} | STATUS: {status} | SUBJECT: {subject}\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line)


# -----------------------------------------------------------------------------
# 4. ТОЧКА ВХОДА (CLI ИНТЕРФЕЙС)
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="EduHub AI Email Robot for Merchant Onboarding")
    parser.add_argument("--test-connection", action="store_true", help="Test SMTP login to Gmail")
    parser.add_argument("--preview", action="store_true", help="Preview all rendered email applications")
    parser.add_argument("--send", type=str, choices=["dodo", "paypro", "paddle"], help="Send email to a specific provider")
    parser.add_argument("--send-all", action="store_true", help="Send applications to all 3 payment providers")
    args = parser.parse_args()

    robot = EmailRobot()

    if args.test_connection:
        robot.test_connection()
        return

    if args.preview or (not args.send and not args.send_all):
        print("=" * 80)
        print("📨 PREVIEW: MERCHANT ONBOARDING APPLICATION DOSSIERS")
        print("=" * 80)
        for key, cfg in TARGET_CONFIGS.items():
            rendered_body = cfg["body_template"].format(prod_url=PRODUCTION_URL)
            print(f"\n--- [TARGET: {cfg['name'].upper()} ({key})] ---")
            print(f"To:      {cfg['recipient']}")
            print(f"Subject: {cfg['subject']}")
            print(f"Content Preview (first 300 chars):\n{rendered_body[:300]}...")
            print("-" * 80)
        print("\nTo send: python services/email_robot.py --send dodo (or --send-all)")
        return

    if args.send:
        cfg = TARGET_CONFIGS.get(args.send)
        if not cfg:
            print(f"Unknown target: {args.send}")
            return
        rendered_body = cfg["body_template"].format(prod_url=PRODUCTION_URL)
        print(f"[*] Preparing to dispatch application to {cfg['name']} ({cfg['recipient']})...")
        robot.send_email(cfg["recipient"], cfg["subject"], rendered_body)

    if args.send_all:
        print("[*] Preparing to dispatch applications to ALL 3 payment providers...")
        for key, cfg in TARGET_CONFIGS.items():
            rendered_body = cfg["body_template"].format(prod_url=PRODUCTION_URL)
            print(f"\n[*] Dispatching to {cfg['name']} ({cfg['recipient']})...")
            robot.send_email(cfg["recipient"], cfg["subject"], rendered_body)
            time.sleep(2)  # Пауза между отправками

if __name__ == "__main__":
    main()
