import os
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone

import app as app_module
import feedback_store
from models import Feedback, Run


def make_run(days_ago: int, run_id: str) -> Run:
    return Run(run_id, date.today() - timedelta(days=days_ago), "strava", 8.0, 42.0, 150, 5.25, 35)


def make_feedback(run: Run) -> Feedback:
    return Feedback(
        run.id,
        run.date,
        run.distance_km,
        run.avg_pace_min_km,
        run.elevation_gain_m,
        3,
        2,
        4,
        "Felt controlled",
        datetime.now(timezone.utc).isoformat(),
    )


class FeedbackManagementTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.old_feedback_path = feedback_store.FEEDBACK_PATH
        self.old_dismissed_path = feedback_store.DISMISSED_PATH
        feedback_store.FEEDBACK_PATH = os.path.join(self.temp_dir, "feedback.json")
        feedback_store.DISMISSED_PATH = os.path.join(self.temp_dir, "dismissed.json")

    def tearDown(self):
        feedback_store.FEEDBACK_PATH = self.old_feedback_path
        feedback_store.DISMISSED_PATH = self.old_dismissed_path

    def test_saved_feedback_can_be_removed_without_deleting_run(self):
        run = make_run(2, "saved-run")
        feedback_store.save(make_feedback(run))
        self.assertTrue(feedback_store.delete(run.id))
        self.assertEqual(feedback_store.load_all(), {})
        self.assertEqual(run.id, "saved-run")

    def test_dismissed_prompt_stays_hidden(self):
        run = make_run(1, "dismissed-run")
        feedback_store.dismiss(run.id)
        visible = app_module._feedback_runs([run], {}, feedback_store.load_dismissed())
        self.assertEqual(visible, [])

    def test_unanswered_prompts_expire_but_saved_feedback_remains(self):
        recent = make_run(7, "recent-run")
        stale = make_run(8, "stale-run")
        visible = app_module._feedback_runs([recent, stale], {stale.id: make_feedback(stale)}, set())
        self.assertEqual([run.id for run in visible], [recent.id, stale.id])
        without_saved = app_module._feedback_runs([recent, stale], {}, set())
        self.assertEqual([run.id for run in without_saved], [recent.id])


if __name__ == "__main__":
    unittest.main()
