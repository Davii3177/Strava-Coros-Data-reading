import os
import tempfile
import unittest

import app as app_module
import recovery_store


class RecoveryCheckinTests(unittest.TestCase):
    def setUp(self):
        self.path = tempfile.mktemp(suffix=".json")
        self.original_path = recovery_store.RECOVERY_PATH
        self.original_runs = app_module._all_runs
        self.original_key = os.environ.pop("OPENAI_API_KEY", None)
        recovery_store.RECOVERY_PATH = self.path
        app_module._all_runs = lambda: []
        app_module.app.config.update(TESTING=True, SECRET_KEY="test-secret")
        self.client = app_module.app.test_client()
        with self.client.session_transaction() as session:
            session["authenticated"] = True

    def tearDown(self):
        recovery_store.RECOVERY_PATH = self.original_path
        app_module._all_runs = self.original_runs
        if self.original_key is not None:
            os.environ["OPENAI_API_KEY"] = self.original_key
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_valid_checkin_is_saved_with_safe_guidance(self):
        response = self.client.post("/api/recovery/checkins", json={
            "body_areas": ["knees"], "pain_level": 4, "onset": "gradual",
            "sensation": ["sore"], "triggers": ["running"], "notes": "After a longer run.",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json["urgent"])
        self.assertIn("not a diagnosis", response.json["guidance"])
        self.assertEqual(len(recovery_store.load_all()), 1)

    def test_red_flag_bypasses_normal_guidance(self):
        response = self.client.post("/api/recovery/checkins", json={
            "body_areas": ["chest"], "pain_level": 7, "onset": "sudden",
            "sensation": ["sharp"], "triggers": ["rest"], "notes": "Chest pain and trouble breathing.",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["urgent"])
        self.assertIn("urgent care", response.json["guidance"].lower())

    def test_rejects_invalid_area_and_pain_level(self):
        response = self.client.post("/api/recovery/checkins", json={
            "body_areas": ["wing"], "pain_level": 15, "sensation": [], "triggers": [],
        })
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
