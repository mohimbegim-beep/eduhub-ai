import unittest
import json
import os
import time
from pathlib import Path
from services.db_engine import init_database, link_telegram_account, get_user_by_telegram, get_connection
from app.main import load_user_balances, save_user_balances

class TestDbAndTgSync(unittest.TestCase):
    def test_database_tables_exist(self):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall()]
            self.assertIn("user_balances", tables)
            self.assertIn("transactions", tables)
            self.assertIn("disputes", tables)
        finally:
            conn.close()

    def test_telegram_account_linking(self):
        test_tg_id = 99887766
        test_token = f"test_session_{int(time.time())}"

        # 1. First save a balance for this token
        balances = load_user_balances()
        balances[test_token] = {
            "email": "student_test@eduhub.ai",
            "tier": "pro_max",
            "balance": 1.0,
            "credits": 50
        }
        save_user_balances(balances)

        # 2. Link Telegram ID
        linked = link_telegram_account(test_tg_id, test_token)
        self.assertIsNotNone(linked)
        self.assertEqual(linked.get("tier"), "pro_max")

        # 3. Retrieve user by Telegram ID
        user_by_tg = get_user_by_telegram(test_tg_id)
        self.assertIsNotNone(user_by_tg)
        self.assertEqual(user_by_tg.get("email"), "student_test@eduhub.ai")

if __name__ == "__main__":
    unittest.main()
