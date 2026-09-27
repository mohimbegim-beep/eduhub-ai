#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EduHub AI — High-Converting Telegram Channel Scraper & Outreach Parser
Target: Active IELTS, English Learning, University & Student Channels in Uzbekistan.
Extracts: Channel Name, Link, Subscribers, Bio, Admin Contact for Ads/Sponsorship.
"""

import os
import re
import json
import csv
import sys
import time
import urllib.request
from typing import Dict, List, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uz;q=0.6"
}

# Curated high-relevance educational channels in Uzbekistan
CANDIDATE_CHANNELS = [
    # Category 1: IELTS & English Language Preparation
    {"username": "ieltszone_uz", "category": "IELTS & English"},
    {"username": "mocktashkent", "category": "IELTS & Mock Tests"},
    {"username": "diyorbeksielts", "category": "IELTS Tutor"},
    {"username": "ielts_boy", "category": "IELTS Tutor"},
    {"username": "ieltswithsherzod", "category": "IELTS Tutor"},
    {"username": "cambridge_lc", "category": "Cambridge Learning"},
    {"username": "registan_lc", "category": "Registan LC"},
    {"username": "everest_lc", "category": "Everest Education"},
    {"username": "ieltsuz", "category": "IELTS Community UZ"},
    {"username": "ingliztili_darslar", "category": "English Lessons UZ"},
    {"username": "uzteachers", "category": "English Teachers UZ"},

    # Category 2: Universities & Student Communities
    {"username": "talabalar_kanali", "category": "University Students"},
    {"username": "talimuz", "category": "Higher Education News"},
    {"username": "piimauz", "category": "Specialized Schools & Agencies"},
    {"username": "abituriyent", "category": "Applicants & Entrants (54k)"},
    {"username": "abituriyentlar_uz", "category": "Abituriyent Live"},
    {"username": "dtm_axborot", "category": "DTM Testing Updates"},
    {"username": "talabagram", "category": "Student Community"},
    {"username": "webster_uz", "category": "Webster University"},
    {"username": "grantlar", "category": "Grants & Scholarships"}
]

def scrape_telegram_channel(username: str, category: str) -> Optional[Dict[str, Any]]:
    clean_username = username.strip().lstrip("@")
    url = f"https://t.me/{clean_username}"
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=6) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return None

    # Title extraction
    title_match = re.search(r'class="tgme_page_title"[^>]*><span[^>]*>(.*?)</span>', html)
    if not title_match:
        title_match = re.search(r'<meta property="og:title" content="(.*?)"', html)
    title = title_match.group(1).strip() if title_match else clean_username

    # Subscribers extraction
    subs_match = re.search(r'class="tgme_page_extra">([^<]+)</div>', html)
    subscribers_str = subs_match.group(1).strip() if subs_match else "N/A"

    # Description / Bio extraction
    desc_match = re.search(r'class="tgme_page_description"[^>]*>(.*?)</div>', html, re.DOTALL)
    if not desc_match:
        desc_match = re.search(r'<meta property="og:description" content="(.*?)"', html)
    
    desc_raw = desc_match.group(1) if desc_match else ""
    desc_clean = re.sub(r'<[^>]+>', ' ', desc_raw).strip()
    desc_clean = " ".join(desc_clean.split())

    # Detect Admin / Contact mentions
    admin_contacts = []
    mentions = re.findall(r'@([a-zA-Z0-9_]{4,32})', desc_clean)
    for m in mentions:
        m_lower = m.lower()
        if m_lower not in [clean_username.lower(), "telegram", "bot"]:
            admin_contacts.append(f"@{m}")

    phones = re.findall(r'(?:\+?998[\s\-]?)?(?:\d{2}[\s\-]?)?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}', desc_clean)
    for p in phones:
        p_clean = re.sub(r'[\s\-]', '', p)
        if len(p_clean) >= 9:
            admin_contacts.append(p)

    primary_contact = admin_contacts[0] if admin_contacts else f"@{clean_username} (Direct/Bio)"

    return {
        "channel_title": title,
        "username": f"@{clean_username}",
        "channel_link": f"https://t.me/{clean_username}",
        "subscribers": subscribers_str,
        "category": category,
        "admin_contact": primary_contact,
        "all_contacts": list(set(admin_contacts)),
        "description": desc_clean[:250] + ("..." if len(desc_clean) > 250 else "")
    }

def run_scraper():
    print("=" * 70)
    print("🚀 EDUHUB AI — ENHANCED TELEGRAM SCRAPER & OUTREACH PARSER")
    print(f"🎯 Scanning {len(CANDIDATE_CHANNELS)} key student & IELTS channels in Uzbekistan...")
    print("=" * 70)
    
    results = []
    for idx, item in enumerate(CANDIDATE_CHANNELS, 1):
        uname = item["username"]
        cat = item["category"]
        print(f"[{idx:02d}/{len(CANDIDATE_CHANNELS)}] Checking @{uname}...", end=" ")
        
        info = scrape_telegram_channel(uname, cat)
        if info and "subscriber" in info["subscribers"]:
            # Parse number of subscribers for filtering
            num_match = re.search(r'([\d\s]+)', info["subscribers"])
            print(f"✅ ACTIVE | {info['subscribers']} | Admin: {info['admin_contact']}")
            results.append(info)
        elif info:
            print(f"ℹ️ {info['subscribers']}")
        else:
            print("⚠️ Skipped / Unavailable")
        time.sleep(0.25)

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)
    json_path = os.path.join(data_dir, "telegram_outreach_targets.json")
    csv_path = os.path.join(data_dir, "telegram_outreach_targets.csv")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    fieldnames = ["channel_title", "username", "subscribers", "category", "admin_contact", "channel_link", "description"]
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print("\n" + "=" * 70)
    print(f"🎉 PARSER FINISHED: Saved {len(results)} high-traffic active channels!")
    print(f"📁 Database JSON: {json_path}")
    print(f"📊 Outreach Sheet (CSV): {csv_path}")
    print("=" * 70)
    return results

if __name__ == "__main__":
    run_scraper()
