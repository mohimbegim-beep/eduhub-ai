"""
EduHub AI — Quality Gate 13: Autonomous AI Agents & Unfinished Work Elimination
Verifies:
1. Autonomous Dunning Sweeper: Automatically revokes unbilled grace access when 3 days lapse.
2. AI Dispute Arbiter Financial Execution: Auto-credits wallet bonus and logs ledger refunds.
3. Autonomous Sweeper Daemon: Coordinates dunning, ephemeral P2P rooms, and periodic snapshots.
4. Autonomous Growth Engine: Generates viral video scripts and 4-language Telegram packs.
5. Sentinel Watchdog Telemetry: Reports live daemon status with sweeper telemetry.
"""

import unittest
import json
import time
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import (
    app,
    USER_BALANCES_FILE,
    TRANSACTIONS_LOG,
    SYSTEM_AUDIT_LOG,
    load_user_balances,
    save_user_balances,
    sweep_expired_dunning_grace_periods
)
from services.autonomous_sweeper import run_autonomous_sweep
from services.autonomous_growth_agent import generate_growth_pack

class TestStage13AutonomousAgents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app, raise_server_exceptions=False)
        cls.root_dir = Path(__file__).resolve().parent.parent

    def test_01_dunning_grace_period_sweeper(self):
        """Verify that expired Dunning Grace Periods are automatically identified and revoked."""
        test_email = f"sweeper_dunning_{int(time.time()*1000)}@eduhub.ai"
        
        # Seed an expired grace period account
        balances = load_user_balances()
        balances[test_email] = {
            "email": test_email,
            "flash_credits": 0,
            "role": "pro_max",
            "tier": "pro_max",
            "is_subscribed": True,
            "subscription": {
                "status": "grace_period",
                "role": "pro_max",
                "dunning": {
                    "active": True,
                    "grace_period_until": time.time() - 3600,  # Expired 1 hour ago
                    "grace_days": 3,
                    "reason": "payment_failed"
                }
            },
            "last_updated": time.time() - 3600
        }
        save_user_balances(balances)

        # Run sweeper
        result = sweep_expired_dunning_grace_periods()
        self.assertEqual(result["status"], "success")
        self.assertGreaterEqual(result["swept_count"], 1)

        # Verify account was downgraded to free_tier
        after_balances = load_user_balances()
        swept_user = after_balances.get(test_email)
        self.assertIsNotNone(swept_user)
        self.assertEqual(swept_user["role"], "free_tier")
        self.assertEqual(swept_user["tier"], "free_tier")
        self.assertFalse(swept_user["is_subscribed"])
        self.assertEqual(swept_user["subscription"]["status"], "expired")
        self.assertFalse(swept_user["subscription"]["dunning"]["active"])

        # Clean up test user
        del after_balances[test_email]
        save_user_balances(after_balances)

    def test_02_dunning_sweep_api_endpoint(self):
        """Verify POST /api/v1/system/dunning/sweep triggers sweeper successfully."""
        res = self.client.post("/api/v1/system/dunning/sweep")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("swept_count", data)

    def test_03_dispute_arbiter_auto_credit_bonus(self):
        """Verify dispute arbiter automatically credits +120% bonus into user wallet and transaction log."""
        test_email = f"dispute_bonus_{int(time.time()*1000)}@eduhub.ai"

        payload = {
            "order_id": f"ord_bonus_{int(time.time())}",
            "customer_email": test_email,
            "plan_tier": "pro_max",
            "issue_type": "accidental_renewal",
            "purchase_date": time.strftime("%Y-%m-%d"),
            "preferred_resolution": "instant_bonus_120",
            "description": "Accidental charge, happy to take platform bonus credit.",
            "language": "ru"
        }

        res = self.client.post("/api/v1/support/dispute-analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["verdict"], "APPROVED_BONUS")

        # Verify user balance was automatically credited
        balances = load_user_balances()
        user = balances.get(test_email)
        self.assertIsNotNone(user, "User was not created/credited in balances")
        self.assertGreaterEqual(user.get("flash_credits", 0), 200)
        self.assertEqual(user.get("role"), "pro_max")
        self.assertEqual(user.get("subscription", {}).get("status"), "active")

        # Verify billing transaction log contains dispute bonus
        if TRANSACTIONS_LOG.exists():
            with open(TRANSACTIONS_LOG, "r", encoding="utf-8") as f:
                txs = json.load(f)
            bonus_txs = [t for t in txs if t.get("customer_email") == test_email and t.get("event_type") == "dispute.bonus_granted"]
            self.assertGreaterEqual(len(bonus_txs), 1, "Dispute bonus transaction was not recorded")

        # Clean up
        if test_email in balances:
            del balances[test_email]
            save_user_balances(balances)

    def test_04_dispute_arbiter_auto_refund_settlement(self):
        """Verify dispute arbiter automatically revokes subscription and logs refund settlement."""
        test_email = f"dispute_refund_{int(time.time()*1000)}@eduhub.ai"

        # Seed active pro user
        balances = load_user_balances()
        balances[test_email] = {
            "email": test_email,
            "flash_credits": 50,
            "role": "pro_max",
            "tier": "pro_max",
            "is_subscribed": True,
            "subscription": {"status": "active", "role": "pro_max"}
        }
        save_user_balances(balances)

        payload = {
            "order_id": f"ord_ref_{int(time.time())}",
            "customer_email": test_email,
            "plan_tier": "pro_max",
            "issue_type": "unhappy_quality",
            "purchase_date": time.strftime("%Y-%m-%d"),
            "preferred_resolution": "card_refund",
            "description": "Requesting card refund under 14-day policy.",
            "language": "en"
        }

        res = self.client.post("/api/v1/support/dispute-analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["verdict"], "APPROVED_NET_REFUND")

        # Verify subscription was revoked
        after_balances = load_user_balances()
        user = after_balances.get(test_email)
        self.assertEqual(user.get("role"), "free_tier")
        self.assertFalse(user.get("is_subscribed"))

        # Clean up
        if test_email in after_balances:
            del after_balances[test_email]
            save_user_balances(after_balances)

    def test_05_autonomous_sweeper_master_service(self):
        """Verify autonomous sweeper master coordinator executes all 3 jobs."""
        res = run_autonomous_sweep()
        self.assertEqual(res["status"], "success")
        self.assertIn("dunning", res)
        self.assertIn("peer_rooms", res)
        self.assertIn("snapshot", res)

    def test_06_autonomous_growth_agent_endpoints(self):
        """Verify Autonomous Growth Engine produces omnichannel assets in 4 languages."""
        res = self.client.get("/api/v1/growth/latest-pack")
        self.assertEqual(res.status_code, 200)
        pack = res.json()
        self.assertIn("viral_video_scripts", pack)
        self.assertGreaterEqual(len(pack["viral_video_scripts"]), 3)
        self.assertIn("telegram_posts", pack)
        
        # Verify all 4 locales exist in marketing pack
        for loc in ["ru", "uz", "en", "es"]:
            self.assertIn(loc, pack["telegram_posts"], f"Missing locale {loc} in growth pack")
            self.assertIn("button_url", pack["telegram_posts"][loc])

        self.assertIn("campus_ambassador_pitch", pack)
        self.assertIn("b2b_tutor_outreach", pack)

    def test_07_sentinel_watchdog_status(self):
        """Verify Sentinel status endpoint reports daemon and sweeper status."""
        res = self.client.get("/api/v1/system/sentinel/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        sentinel = data["sentinel"]
        self.assertTrue(sentinel["is_daemon_alive"])
        self.assertEqual(sentinel["last_status_code"], 200)
        self.assertIn("sweeper", sentinel)

if __name__ == "__main__":
    unittest.main()
