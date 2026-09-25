"""
EduHub AI — Centralized Configuration & Single Source of Truth
Eliminates code duplication and prevents regressions across contacts, pricing, and URLs.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Official Brand & Corporate Contacts (Strictly verified)
BRAND_NAME = "EduHub AI"
CORPORATE_EMAIL = "mahallamade.uz@gmail.com"
OFFICIAL_TELEGRAM_HANDLE = "@mahallamade_m"
OFFICIAL_TELEGRAM_URL = "https://t.me/mahallamade_m"

# Live Production URLs
PRODUCTION_URL = os.getenv("PRODUCTION_URL", "https://eduhub-ai.onrender.com").rstrip("/")

# Dodo Payments Merchant of Record URLs & Product IDs
DODO_CHECKOUT_PRO_MAX = os.getenv(
    "DODO_CHECKOUT_PRO_MAX",
    "https://checkout.dodopayments.com/buy/pdt_0No9KRSRGMZyhypjqIEfu?quantity=1&redirect_url=https://eduhub-ai.onrender.com%2Fstatic%2Fpayment-success.html"
)
DODO_CHECKOUT_ATS = os.getenv(
    "DODO_CHECKOUT_ATS",
    "https://checkout.dodopayments.com/buy/pdt_0NoLUjhcuEzS9BBgujRcS?quantity=1&redirect_url=https://eduhub-ai.onrender.com%2Fstatic%2Fpayment-success.html"
)
DODO_CHECKOUT_BLUEPRINT = os.getenv(
    "DODO_CHECKOUT_BLUEPRINT",
    "https://checkout.dodopayments.com/buy/pdt_0NoLUjhcuEzS9BBgujRcS?quantity=1&redirect_url=https://eduhub-ai.onrender.com%2Fstatic%2Fpayment-success.html"
)
