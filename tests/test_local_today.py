"""Regression tests for the runner-local-date bug: a server running in UTC
(as most cloud hosts do) rolls its calendar date over to the next day hours
before midnight in US/EU timezones, which silently showed tomorrow's
scheduled workout for the back half of the runner's evening.
"""
import unittest
from datetime import date, datetime, timezone
from unittest.mock import patch
from zoneinfo import ZoneInfo

import app as app_module


class LocalTodayTests(unittest.TestCase):
    def setUp(self):
        self.original_tz = app_module.os.environ.pop("RUNNER_TIMEZONE", None)

    def tearDown(self):
        if self.original_tz is not None:
            app_module.os.environ["RUNNER_TIMEZONE"] = self.original_tz
        else:
            app_module.os.environ.pop("RUNNER_TIMEZONE", None)

    def test_runner_timezone_fixes_the_rollover(self):
        """With RUNNER_TIMEZONE set, a UTC server clock that already reads
        Saturday must still resolve to Friday for a New York runner."""
        app_module.os.environ["RUNNER_TIMEZONE"] = "America/New_York"
        saturday_3am_utc = datetime(2026, 7, 18, 3, 0, tzinfo=timezone.utc)

        real_datetime = datetime

        class FrozenDatetime(real_datetime):
            @classmethod
            def now(cls, tz=None):
                if tz is None:
                    return saturday_3am_utc.replace(tzinfo=None)
                return saturday_3am_utc.astimezone(tz)

        with patch.object(app_module, "datetime", FrozenDatetime):
            local_today = app_module._today()

        self.assertEqual(local_today, date(2026, 7, 17))  # Friday, not Saturday
        self.assertEqual(local_today.strftime("%A"), "Friday")

    def test_unset_runner_timezone_falls_back_to_server_date(self):
        self.assertNotIn("RUNNER_TIMEZONE", app_module.os.environ)
        self.assertEqual(app_module._today(), date.today())

    def test_invalid_runner_timezone_falls_back_gracefully(self):
        app_module.os.environ["RUNNER_TIMEZONE"] = "Not/ARealZone"
        self.assertEqual(app_module._today(), date.today())

    def test_valid_timezone_matches_zoneinfo_directly(self):
        app_module.os.environ["RUNNER_TIMEZONE"] = "America/New_York"
        expected = datetime.now(ZoneInfo("America/New_York")).date()
        self.assertEqual(app_module._today(), expected)


if __name__ == "__main__":
    unittest.main()
