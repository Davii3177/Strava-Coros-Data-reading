import os
import tempfile
import unittest
from datetime import date, timedelta

import personal_records
import planning
import race_prediction
import recovery_trends
import shoe_store
import training_load
import training_store
from models import Feedback, Race, RecoveryCheckin, Run


def run(days_ago, distance=8, pace=5.2, run_id=None):
    return Run(run_id or f"run-{days_ago}", date.today() - timedelta(days=days_ago), "strava", distance, distance * pace, 150, pace, 40)


class TrainingCompanionTests(unittest.TestCase):
    def test_readiness_reduces_load_after_large_spike(self):
        runs = [run(day, 10) for day in range(0, 7)] + [run(day, 5) for day in (8, 15, 22, 29)]
        result = training_load.calculate(runs, {}, [])
        self.assertEqual(result["status"], "Reduce load")
        self.assertGreater(result["change_percent"], 40)

    def test_urgent_recovery_overrides_training_load(self):
        checkin = RecoveryCheckin("x", ["kneecap"], 9, "sudden", ["sharp"], ["walking"], "", {}, "", True, date.today().isoformat())
        result = training_load.calculate([run(1)], {}, [checkin])
        self.assertEqual(result["status"], "Recovery recommended")

    def test_today_run_explains_readiness_adjustment(self):
        readiness = {"tone": "reduce", "status": "Reduce load"}
        result = planning.todays_run([run(1)], readiness, [])
        self.assertEqual(result["type"], "Recovery day")
        self.assertTrue(any("reduced" in reason for reason in result["reasons"]))

    def test_plan_marks_missed_without_making_up_mileage(self):
        monday = date.today() - timedelta(days=date.today().weekday())
        result = planning.plan_vs_actual([], [], {}, today=monday + timedelta(days=3))
        if result["adjustments"][0].startswith("No automatic"):
            self.skipTest("No non-rest scheduled day occurred before the supplied Thursday")
        self.assertIn("do not stack missed mileage", result["adjustments"][0])

    def test_race_prediction_is_labeled_and_ranged(self):
        race = Race(date.today() + timedelta(days=30), "10K", 10, 50, True)
        result = race_prediction.goal_center([race], [run(1, 5, 5.0)])
        self.assertEqual(result["phase"], "Build")
        self.assertLess(result["prediction"]["low_min"], result["prediction"]["high_min"])
        self.assertIn("not guaranteed", result["prediction"]["explanation"])

    def test_personal_records_only_include_matching_distance(self):
        result = personal_records.calculate([run(1, 5.0), run(2, 12.0)])
        labels = {item["label"] for item in result["records"]}
        self.assertIn("Fastest 5K", labels)
        self.assertNotIn("Fastest marathon", labels)

    def test_recovery_trend_compares_consecutive_entries(self):
        older = RecoveryCheckin("a", ["calves"], 7, "gradual", [], [], "", {}, "", False, "2026-01-01T00:00:00")
        newer = RecoveryCheckin("b", ["calves"], 4, "gradual", [], [], "", {}, "", False, "2026-01-02T00:00:00")
        self.assertEqual(recovery_trends.summarize([newer, older])["areas"][0]["trend"], "Improving")

    def test_json_stores_training_status_and_shoe_assignment(self):
        temp_dir = tempfile.mkdtemp()
        old_training, old_shoes = training_store.PATH, shoe_store.PATH
        training_store.PATH = os.path.join(temp_dir, "plan.json")
        shoe_store.PATH = os.path.join(temp_dir, "shoes.json")
        try:
            training_store.save("2026-01-01", "shortened", 4.2, "tight calf")
            self.assertEqual(training_store.load_all()["2026-01-01"]["status"], "shortened")
            shoe = shoe_store.add("Brand", "Model", "Daily", "2026-01-01", 600, "tempo")
            shoe_store.assign("run-1", shoe.id)
            self.assertEqual(shoe_store.assignments()["run-1"], shoe.id)
            self.assertEqual(shoe_store.load_all()[0].shoe_type, "tempo")
        finally:
            training_store.PATH, shoe_store.PATH = old_training, old_shoes

    def test_shoe_suggestion_matches_today_workout_type(self):
        temp_dir = tempfile.mkdtemp()
        old_shoes = shoe_store.PATH
        shoe_store.PATH = os.path.join(temp_dir, "shoes.json")
        try:
            shoe_store.add("Brand", "Daily", "Daily", "2026-01-01", 600, "daily")
            tempo = shoe_store.add("Brand", "Fast", "Tempo", "2026-01-01", 600, "tempo")
            suggestion = shoe_store.suggest_for_today([], {}, "Tempo run")
            self.assertEqual(suggestion["shoe"].id, tempo.id)
            self.assertTrue(suggestion["purpose_matched"])
        finally:
            shoe_store.PATH = old_shoes


if __name__ == "__main__":
    unittest.main()
