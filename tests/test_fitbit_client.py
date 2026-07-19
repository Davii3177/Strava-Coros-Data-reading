import unittest
from unittest.mock import patch

import fitbit_client


class FitbitClientConfigurationTests(unittest.TestCase):
    def test_unconfigured_recovery_fetchers_return_no_measurements(self):
        with (
            patch.object(fitbit_client, "is_configured", return_value=False),
            patch.object(fitbit_client, "_get_points") as get_points,
        ):
            self.assertEqual(fitbit_client.fetch_sleep(), [])
            self.assertEqual(fitbit_client.fetch_resting_hr(), [])
            self.assertEqual(fitbit_client.fetch_hrv(), [])

        get_points.assert_not_called()

    def test_unconfigured_activity_fetch_keeps_explicit_sample_runs(self):
        with patch.object(fitbit_client, "is_configured", return_value=False):
            runs = fitbit_client.fetch_runs(limit=2)

        self.assertEqual(len(runs), 2)
        self.assertTrue(all(run.source == "fitbit" for run in runs))
        self.assertTrue(all(run.id.startswith("fitbit-sample-") for run in runs))


if __name__ == "__main__":
    unittest.main()
