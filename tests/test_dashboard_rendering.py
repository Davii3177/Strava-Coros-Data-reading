import unittest
from contextlib import ExitStack
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from unittest.mock import patch

import app as app_module
from models import Feedback, Race, RecoveryCheckin, Run, Shoe


class MarkupProbe(HTMLParser):
    """Collect semantic markup without depending on an HTML test library."""

    def __init__(self):
        super().__init__()
        self.elements = []
        self.elements_by_id = {}
        self.forms = []
        self.links = []
        self.scripts = []
        self.stylesheets = []
        self.images = []
        self.controls = []
        self.classes = set()
        self.data_attributes = set()
        self.text_parts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.elements.append((tag, attributes))
        element_id = attributes.get("id")
        if element_id:
            self.elements_by_id[element_id] = (tag, attributes)
        self.classes.update(attributes.get("class", "").split())

        self.data_attributes.update(
            name for name in attributes if name.startswith("data-")
        )
        if tag == "form":
            self.forms.append(attributes)
        elif tag == "a":
            self.links.append(attributes)
        elif tag == "script" and attributes.get("src"):
            self.scripts.append(attributes["src"])
        elif (
            tag == "link"
            and attributes.get("rel") == "stylesheet"
            and attributes.get("href")
        ):
            self.stylesheets.append(attributes["href"])
        elif tag == "img":
            self.images.append(attributes)
        elif tag in {"button", "input", "select", "textarea"}:
            self.controls.append((tag, attributes))

    def handle_data(self, data):
        if data.strip():
            self.text_parts.append(data.strip())

    @property
    def text(self):
        return " ".join(" ".join(self.text_parts).split())


def parse(response):
    probe = MarkupProbe()
    probe.feed(response.get_data(as_text=True))
    return probe


class DashboardRenderingContractTests(unittest.TestCase):
    def setUp(self):
        self.old_testing = app_module.app.config.get("TESTING")
        self.old_secret = app_module.app.config.get("SECRET_KEY")
        app_module.app.config.update(TESTING=True, SECRET_KEY="render-test-secret")

        today = date.today()
        self.runs = [
            Run(
                "sample-strava-render",
                today - timedelta(days=1),
                "strava",
                8.2,
                43.1,
                151,
                5.26,
                72,
            ),
            Run(
                "sample-coros-render",
                today - timedelta(days=2),
                "coros",
                5.0,
                28.0,
                143,
                5.6,
                41,
            ),
        ]
        self.feedback = Feedback(
            run_id=self.runs[0].id,
            date=self.runs[0].date,
            distance_km=self.runs[0].distance_km,
            avg_pace_min_km=self.runs[0].avg_pace_min_km,
            elevation_gain_m=self.runs[0].elevation_gain_m,
            difficulty=3,
            soreness=2,
            motivation=4,
            comment="Comfortable sample effort",
            submitted_at=datetime.now(timezone.utc).isoformat(),
        )
        self.race = Race(
            date=today + timedelta(days=30),
            name="Sample 10K",
            distance_km=10,
            target_time_min=50,
            priority=True,
        )
        self.checkin = RecoveryCheckin(
            id="sample-checkin-render",
            body_areas=["calves"],
            pain_level=3,
            onset="gradual",
            sensation=["tight"],
            triggers=["running"],
            notes="Mild tightness",
            training_context={},
            guidance="Educational sample guidance; not a diagnosis.",
            urgent=False,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self.shoe = Shoe(
            id="sample-shoe-render",
            brand="Sample",
            model="Daily Trainer",
            nickname="Daily",
            purchase_date=today.isoformat(),
            replacement_km=600,
        )

        self.patches = ExitStack()
        self.patches.enter_context(
            patch.object(app_module, "_all_runs", return_value=self.runs)
        )
        self.patches.enter_context(
            patch.object(
                app_module.feedback_store,
                "load_all",
                return_value={self.feedback.run_id: self.feedback},
            )
        )
        self.patches.enter_context(
            patch.object(
                app_module.feedback_store, "load_dismissed", return_value=set()
            )
        )
        self.patches.enter_context(
            patch.object(app_module.race_store, "load_all", return_value=[self.race])
        )
        self.patches.enter_context(
            patch.object(
                app_module.recovery_store, "load_all", return_value=[self.checkin]
            )
        )
        self.patches.enter_context(
            patch.object(app_module.training_store, "load_all", return_value={})
        )
        self.patches.enter_context(
            patch.object(
                app_module.shoe_store,
                "with_mileage",
                return_value=[
                    {
                        "shoe": self.shoe,
                        "mileage_km": self.runs[0].distance_km,
                        "replacement_percent": 1,
                        "average_pace": self.runs[0].avg_pace_min_km,
                        "average_soreness": self.feedback.soreness,
                    }
                ],
            )
        )
        self.patches.enter_context(
            patch.object(app_module.shoe_store, "assignments", return_value={})
        )
        self.client = app_module.app.test_client()

    def tearDown(self):
        self.patches.close()
        app_module.app.config.update(
            TESTING=self.old_testing, SECRET_KEY=self.old_secret
        )

    def authenticate(self):
        with self.client.session_transaction() as session:
            session["authenticated"] = True

    def assert_local_images(self, probe, expected_sources):
        sources = {image.get("src") for image in probe.images}
        self.assertEqual(sources, expected_sources)
        for image in probe.images:
            source = image.get("src", "")
            self.assertTrue(source.startswith("/static/images/"), source)
            self.assertTrue(image.get("alt", "").strip())
            self.assertGreater(int(image.get("width", "0")), 0)
            self.assertGreater(int(image.get("height", "0")), 0)
            asset = self.client.get(source)
            self.assertEqual(asset.status_code, 200)
            self.assertTrue(asset.mimetype.startswith("image/"))
            self.assertGreater(len(asset.data), 0)
            asset.close()

    def test_authenticated_dashboard_renders_sample_runs(self):
        self.authenticate()

        response = self.client.get("/")
        probe = parse(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/html")
        self.assertIn("8.2 km", probe.text)
        self.assertIn("5.0 km", probe.text)
        self.assertIn("Sample 10K", probe.text)
        run_links = {link.get("href") for link in probe.links}
        self.assertIn("/runs/sample-strava-render", run_links)
        self.assertIn("/runs/sample-coros-render", run_links)
        self.assertNotIn("password", probe.elements_by_id)
        self.assert_local_images(
            probe,
            {"/static/images/gaman-mountain-valley.jpg"},
        )

    def test_dashboard_preserves_sections_forms_hooks_and_scripts(self):
        self.authenticate()

        response = self.client.get("/")
        probe = parse(response)

        required_ids = {
            "daily",
            "readiness",
            "goal-center",
            "personal-records",
            "plan-actual",
            "activity-analysis",
            "shoes",
            "recovery-timeline",
            "pace-trends",
            "runs",
            "calendar",
            "recovery",
            "workouts",
            "feedback",
            "races",
            "about",
            "recovery-form",
            "selected-areas",
            "pain-output",
            "pain-level",
            "guidance-result",
        }
        self.assertTrue(
            required_ids.issubset(probe.elements_by_id),
            f"Missing required IDs: {sorted(required_ids - probe.elements_by_id.keys())}",
        )

        required_hooks = {
            "data-expand-all",
            "data-compact-all",
            "data-run-panel",
            "data-default-limit",
            "data-run-search",
            "data-panel-toggle",
            "data-run-list",
            "data-run-item",
            "data-search",
            "data-area",
        }
        self.assertTrue(
            required_hooks.issubset(probe.data_attributes),
            f"Missing data hooks: {sorted(required_hooks - probe.data_attributes)}",
        )

        form_actions = {form.get("action") for form in probe.forms}
        required_actions = {
            "/training/today",
            "/races",
            f"/races/{self.race.date.isoformat()}/delete",
            "/shoes",
            f"/shoes/{self.shoe.id}/retire",
            f"/runs/{self.runs[0].id}/shoe",
            f"/recovery/{self.checkin.id}/adherence",
            f"/feedback/{self.runs[0].id}",
            f"/feedback/{self.runs[0].id}/delete",
            f"/feedback/{self.runs[1].id}",
            f"/feedback/{self.runs[1].id}/dismiss",
        }
        self.assertTrue(
            required_actions.issubset(form_actions),
            f"Missing form actions: {sorted(required_actions - form_actions)}",
        )

        recovery_form_tag, recovery_form = probe.elements_by_id["recovery-form"]
        self.assertEqual(recovery_form_tag, "form")
        self.assertEqual(recovery_form.get("class"), "recovery-form")
        control_names = {
            attrs.get("name") for _, attrs in probe.controls if attrs.get("name")
        }
        self.assertTrue(
            {
                "status",
                "actual_distance_km",
                "pain_level",
                "onset",
                "sensation",
                "triggers",
                "notes",
                "difficulty",
                "soreness",
                "motivation",
                "comment",
            }.issubset(control_names)
        )
        _, guidance_result = probe.elements_by_id["guidance-result"]
        self.assertEqual(guidance_result.get("aria-live"), "polite")

        required_scripts = {
            "/static/dashboard_compact.js",
            "/static/run_panels.js",
            "/static/recovery.js",
        }
        self.assertTrue(required_scripts.issubset(set(probe.scripts)))
        self.assertNotIn("theme-toggle", probe.elements_by_id)
        self.assertNotIn("/static/theme.js", probe.scripts)
        self.assertTrue(
            any(href.startswith("/static/style.css") for href in probe.stylesheets)
        )
        self.assertIn("dashboard-wordmark", probe.classes)
        self.assertIn("dashboard-view-menu", probe.classes)
        self.assertIn("dashboard-secondary-heading", probe.classes)
        self.assertIn("workout-insights", probe.classes)
        self.assertIn("Run with clarity", probe.text)
        section_order = list(probe.elements_by_id)
        self.assertLess(section_order.index("daily"), section_order.index("readiness"))
        self.assertLess(section_order.index("readiness"), section_order.index("plan-actual"))

        compact_response = self.client.get("/static/dashboard_compact.js")
        compact_script = compact_response.get_data(as_text=True)
        compact_response.close()
        default_set = compact_script.split("]);", 1)[0]
        self.assertNotIn('"plan-actual"', default_set)
        self.assertIn('"goal-center"', default_set)
        self.assertIn('"workouts"', default_set)

    def test_unauthenticated_login_renders_required_controls(self):
        response = self.client.get("/")
        probe = parse(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/html")
        self.assertIn("password", probe.elements_by_id)
        password_tag, password = probe.elements_by_id["password"]
        self.assertEqual(password_tag, "input")
        self.assertEqual(password.get("type"), "password")
        self.assertEqual(password.get("name"), "password")
        self.assertIn("required", password)
        self.assertTrue(
            any(form.get("method", "get").lower() == "post" for form in probe.forms)
        )
        self.assertTrue(
            any("compact-login" in form.get("class", "").split() for form in probe.forms)
        )
        self.assertTrue(
            any(
                tag == "button" and attrs.get("type") == "submit"
                for tag, attrs in probe.controls
            )
        )
        hrefs = {link.get("href") for link in probe.links}
        self.assertIn(
            "https://github.com/Davii3177/Strava-Coros-Data-reading", hrefs
        )
        self.assertIn("mailto:davidch3@andrew.cmu.edu", hrefs)
        self.assertIn("#access", hrefs)
        self.assertIn("#about", hrefs)
        self.assertIn("/static/landing.js", probe.scripts)
        self.assertTrue(
            any(href.startswith("/static/style.css") for href in probe.stylesheets)
        )
        self.assertNotIn("theme-toggle", probe.elements_by_id)
        self.assertNotIn("/static/theme.js", probe.scripts)
        self.assert_local_images(
            probe, {"/static/images/gaman-mountain-road-hero.jpg"}
        )
        self.assertIn("Run with clarity", probe.text)
        self.assertIn("After at least five feedback entries", probe.text)
        self.assertIn("inspectable linear regression", probe.text)
        self.assertIn("See the story behind the miles", probe.text)
        self.assertIn("From activity file to next run", probe.text)
        self.assertIn("API credentials are never placed in the browser", probe.text)
        self.assertIn("never a diagnosis", probe.text)
        self.assertIn("Every run moves the plan forward", probe.text)
        self.assertIn("landing-about-visual", probe.classes)
        self.assertIn("about-route-map", probe.classes)
        self.assertIn("Two systems. Two clearly defined jobs", probe.text)
        self.assertIn("Predicted difficulty", probe.text)
        self.assertIn("Minimum five rated runs", probe.text)
        self.assertIn("Urgent symptoms bypass ordinary AI guidance", probe.text)
        self.assertIn("no confidence interval", probe.text)
        dialog_tag, dialog = probe.elements_by_id["login-dialog"]
        self.assertEqual(dialog_tag, "dialog")
        self.assertEqual(dialog.get("aria-labelledby"), "login-dialog-title")
        self.assertEqual(dialog.get("data-auto-open"), "false")
        self.assertNotIn("open", dialog)
        self.assertGreaterEqual(
            sum(1 for _, attrs in probe.elements if "data-login-open" in attrs), 2
        )
        self.assertEqual(
            sum(1 for _, attrs in probe.elements if "data-about-benefit" in attrs), 3
        )
        disclosures = [
            (tag, attrs)
            for tag, attrs in probe.elements
            if "data-about-disclosure" in attrs
        ]
        self.assertEqual(len(disclosures), 3)
        self.assertTrue(all(tag == "details" and "open" not in attrs for tag, attrs in disclosures))
        self.assertNotIn("Run farther. Recover smarter.", probe.text)
        self.assertNotIn("landing-story", probe.classes)
        self.assertNotIn("daily", probe.elements_by_id)

    def test_failed_login_marks_dialog_for_auto_open(self):
        with patch.dict(app_module.os.environ, {"APP_PASSWORD": "expected-password"}):
            response = self.client.post("/", data={"password": "wrong-password"})
        probe = parse(response)

        self.assertEqual(response.status_code, 200)
        _, dialog = probe.elements_by_id["login-dialog"]
        self.assertEqual(dialog.get("data-auto-open"), "true")
        self.assertTrue(any(attrs.get("role") == "alert" for _, attrs in probe.elements))
        self.assertIn("Incorrect password", probe.text)

    def test_run_detail_renders_for_an_authenticated_sample_run(self):
        self.authenticate()

        response = self.client.get(f"/runs/{self.runs[0].id}")
        probe = parse(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn(str(self.runs[0].date), probe.text)
        self.assertIn("8.2 km", probe.text)
        self.assertIn(self.runs[0].pace_str, probe.text)
        self.assertIn("151", probe.text)
        self.assertIn("72 m", probe.text)
        self.assertIn("What went well", probe.text)
        self.assertIn(
            "Log subjective feedback so future recommendations can account for how this effort felt.",
            probe.text,
        )
        self.assertIn(
            "Use an easy or rest day next if this effort felt hard", probe.text
        )
        self.assertIn(
            "/#activity-analysis", {link.get("href") for link in probe.links}
        )
        self.assertTrue(
            any(href.startswith("/static/style.css") for href in probe.stylesheets)
        )
        self.assert_local_images(probe, {"/static/images/gaman-ridge-runner.jpg"})
        self.assertNotIn("theme-toggle", probe.elements_by_id)
        self.assertNotIn("/static/theme.js", probe.scripts)


if __name__ == "__main__":
    unittest.main()
