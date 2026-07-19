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
        self.videos = []
        self.video_sources = []
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
        elif tag == "video":
            self.videos.append(attributes)
        elif tag == "source":
            self.video_sources.append(attributes)
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
        self.patches.enter_context(
            patch.object(
                app_module,
                "_recovery_metrics",
                return_value={
                    "sleep": app_module.fitbit_client._sample_sleep(3),
                    "resting_hr": app_module.fitbit_client._sample_resting_hr(7),
                    "hrv": [],
                },
            )
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

    def assert_landing_video(self, probe):
        self.assertEqual(len(probe.videos), 1)
        video = probe.videos[0]
        for attribute in ("autoplay", "muted", "loop", "playsinline"):
            self.assertIn(attribute, video)
        self.assertEqual(video.get("aria-hidden"), "true")
        self.assertEqual(
            video.get("poster"), "/static/images/gaman-0716-poster-v2.jpg"
        )
        self.assertEqual(
            probe.video_sources,
            [
                {"src": "/static/videos/gaman-0716-hero-compressed.mp4", "type": "video/mp4"},
            ],
        )
        for source in probe.video_sources:
            asset = self.client.get(source["src"])
            self.assertEqual(asset.status_code, 200)
            self.assertTrue(asset.mimetype.startswith("video/"))
            self.assertGreater(len(asset.data), 0)
            asset.close()

    def test_authenticated_dashboard_renders_sample_runs(self):
        self.authenticate()

        response = self.client.get("/")
        probe = parse(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/html")
        self.assertIn("Today's run", probe.text)
        self.assertIn("13.2 km", probe.text)
        self.assertIn("Ready to train", probe.text)
        product_links = {link.get("href") for link in probe.links}
        self.assertTrue({"/training", "/activities", "/recovery", "/profile"}.issubset(product_links))
        self.assertNotIn("password", probe.elements_by_id)
        self.assert_local_images(probe, set())

    def test_dashboard_preserves_sections_forms_hooks_and_scripts(self):
        self.authenticate()

        routes = ["/", "/training", "/activities", "/recovery", "/profile"]
        probes = [parse(self.client.get(route)) for route in routes]
        element_ids = set().union(*(set(probe.elements_by_id) for probe in probes))

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
            required_ids.issubset(element_ids),
            f"Missing required IDs: {sorted(required_ids - element_ids)}",
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
        data_attributes = set().union(*(probe.data_attributes for probe in probes))
        required_hooks -= {"data-expand-all", "data-compact-all"}
        self.assertTrue(required_hooks.issubset(data_attributes), f"Missing data hooks: {sorted(required_hooks - data_attributes)}")

        form_actions = {form.get("action") for probe in probes for form in probe.forms}
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

        recovery_probe = probes[3]
        recovery_form_tag, recovery_form = recovery_probe.elements_by_id["recovery-form"]
        self.assertEqual(recovery_form_tag, "form")
        self.assertEqual(recovery_form.get("class"), "recovery-form")
        control_names = {
            attrs.get("name") for probe in probes for _, attrs in probe.controls if attrs.get("name")
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
        _, guidance_result = recovery_probe.elements_by_id["guidance-result"]
        self.assertEqual(guidance_result.get("aria-live"), "polite")

        required_scripts = {
            "/static/dashboard_compact.js",
            "/static/run_panels.js",
            "/static/recovery.js",
        }
        scripts = {script for probe in probes for script in probe.scripts}
        self.assertTrue(required_scripts.issubset(scripts))
        self.assertTrue(all("theme-toggle" not in probe.elements_by_id for probe in probes))
        self.assertNotIn("/static/theme.js", scripts)
        self.assertTrue(
            all(any(href.startswith("/static/style.css") for href in probe.stylesheets) for probe in probes)
        )
        classes = set().union(*(probe.classes for probe in probes))
        self.assertIn("dashboard-wordmark", classes)
        self.assertIn("mobile-product-nav", classes)
        self.assertIn("dashboard-secondary-heading", classes)
        self.assertIn("workout-insights", classes)
        self.assertIn("Overview", probes[0].text)
        section_order = list(probes[0].elements_by_id)
        self.assertLess(section_order.index("daily"), section_order.index("readiness"))
        for route, probe in zip(routes, probes):
            active = [link for link in probe.links if link.get("aria-current") == "page"]
            self.assertGreaterEqual(len(active), 1, route)

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
            probe, {"/static/images/gaman-mountain-valley.jpg"}
        )
        self.assert_landing_video(probe)
        self.assertIn("Run today, or rest?", probe.text)
        self.assertIn("Sore quads", probe.text)
        self.assertIn("Your activity becomes a decision you can inspect", probe.text)
        self.assertIn("Honest limits where it does not", probe.text)
        self.assertIn("A running workspace built around the data", probe.text)
        self.assertIn("/how-it-works", hrefs)
        dialog_tag, dialog = probe.elements_by_id["login-dialog"]
        self.assertEqual(dialog_tag, "dialog")
        self.assertEqual(dialog.get("aria-labelledby"), "login-dialog-title")
        self.assertEqual(dialog.get("data-auto-open"), "false")
        self.assertNotIn("open", dialog)
        self.assertGreaterEqual(
            sum(1 for _, attrs in probe.elements if "data-login-open" in attrs), 2
        )
        self.assertIn("landing-preview-card", probe.classes)
        self.assertIn("Ready to train", probe.text)
        self.assertNotIn("Run farther. Recover smarter.", probe.text)
        self.assertNotIn("landing-story", probe.classes)
        self.assertNotIn("daily", probe.elements_by_id)

    def test_how_it_works_explains_model_boundaries(self):
        response = self.client.get("/how-it-works")
        probe = parse(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Direct activity data", probe.text)
        self.assertIn("Rule-based calculations", probe.text)
        self.assertIn("Statistical model", probe.text)
        self.assertIn("Optional language model", probe.text)
        self.assertIn("After at least five rated runs", probe.text)
        self.assertIn("Urgent symptoms bypass ordinary guidance", probe.text)
        self.assertIn("No diagnosis or emergency care", probe.text)

    def test_research_page_renders_the_literature_review(self):
        response = self.client.get("/research")
        probe = parse(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Running-Related Pain and Soreness", probe.text)
        self.assertIn("110", probe.text)
        # All 13 anatomical regions are anchored for deep links.
        for region in range(13):
            self.assertIn(f"region-{region}", probe.elements_by_id, f"region-{region}")
        # The evidence tables are wrapped in scrollable containers.
        self.assertIn("table-wrap", probe.classes)
        self.assertIn("Evidence-Based Treatment Matrix by Condition", probe.text)
        self.assertIn("Red Flags and Triage", probe.text)
        # The landing page links to it.
        landing = parse(self.client.get("/"))
        self.assertIn("/research", {link.get("href") for link in landing.links})

    def test_failed_login_marks_dialog_for_auto_open(self):
        with patch.dict(app_module.os.environ, {"APP_PASSWORD": "expected-password"}):
            response = self.client.post("/", data={"password": "wrong-password"})
        probe = parse(response)

        self.assertEqual(response.status_code, 200)
        _, dialog = probe.elements_by_id["login-dialog"]
        self.assertEqual(dialog.get("data-auto-open"), "true")
        self.assertTrue(any(attrs.get("role") == "alert" for _, attrs in probe.elements))
        self.assertIn("Incorrect password", probe.text)

    def test_product_areas_are_protected_and_responsive_navigation_is_defined(self):
        for route in ("/training", "/activities", "/recovery", "/profile"):
            response = self.client.get(route)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.headers["Location"].endswith("/"))

        style_response = self.client.get("/static/style.css")
        stylesheet = style_response.get_data(as_text=True)
        style_response.close()
        self.assertIn(".mobile-product-nav", stylesheet)
        self.assertIn("@media (max-width: 900px)", stylesheet)
        self.assertIn("@media (prefers-reduced-motion: reduce)", stylesheet)
        self.assertIn("Contrast guarantee", stylesheet)
        self.assertIn(".dashboard-body .readiness-card strong", stylesheet)
        self.assertIn(".login-dialog-submit", stylesheet)
        self.assertIn(".detail-body .metric-card:nth-child(2)", stylesheet)

    def test_all_pages_use_the_contrast_stylesheet_revision(self):
        public_routes = ("/", "/how-it-works")
        for route in public_routes:
            probe = parse(self.client.get(route))
            self.assertTrue(all("recovery-metrics-20260718" in href for href in probe.stylesheets))

        self.authenticate()
        for route in ("/", "/training", "/activities", "/recovery", "/profile", f"/runs/{self.runs[0].id}"):
            probe = parse(self.client.get(route))
            self.assertTrue(all("recovery-metrics-20260718" in href for href in probe.stylesheets), route)

    def test_recovery_page_shows_measured_recovery_data(self):
        self.authenticate()
        body = self.client.get("/recovery").get_data(as_text=True)
        self.assertIn("Measured recovery data", body)
        self.assertIn("asleep", body)  # sleep summary tile
        self.assertIn("Resting heart rate", body)
        self.assertIn("bpm", body)
        # HRV has no sample data, so its unavailable state should render
        self.assertIn("Not synced from your devices.", body)

    def test_ask_gaman_widget_is_present_on_dashboard(self):
        self.authenticate()
        probe = parse(self.client.get("/"))
        self.assertIn("ask-panel", probe.elements_by_id)
        self.assertEqual(probe.elements_by_id["ask-panel"][0], "dialog")
        self.assertIn("data-ask-open", probe.data_attributes)
        self.assertIn("/static/ask.js", probe.scripts)

    def test_ask_endpoint_requires_authentication(self):
        response = self.client.post("/api/ask", json={"question": "Should I run today?"})
        self.assertEqual(response.status_code, 401)

    def test_ask_endpoint_rejects_an_empty_question(self):
        self.authenticate()
        response = self.client.post("/api/ask", json={"question": "   "})
        self.assertEqual(response.status_code, 400)

    def test_ask_endpoint_reports_when_not_configured(self):
        self.authenticate()
        with patch.dict(app_module.os.environ, {}, clear=False):
            app_module.os.environ.pop("GEMINI_API_KEY", None)
            response = self.client.post("/api/ask", json={"question": "Should I run today?"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data["ok"])
        self.assertIn("GEMINI_API_KEY", data["answer"])

    def test_ask_endpoint_returns_a_grounded_answer_when_configured(self):
        self.authenticate()
        with patch.dict(app_module.os.environ, {"GEMINI_API_KEY": "test-key"}), patch.object(
            app_module, "_ask_gemini", return_value="Keep today easy: an easy 5 km."
        ) as fake_model:
            response = self.client.post(
                "/api/ask", json={"question": "What should I run today?", "history": []}
            )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["ok"])
        self.assertIn("easy 5 km", data["answer"])
        # The model must be called with a grounded context containing the runner's readiness.
        self.assertTrue(fake_model.called)
        context_arg = fake_model.call_args.args[2]
        self.assertIn("readiness", context_arg)
        self.assertIn("recent_runs", context_arg)

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
            "/activities#activity-analysis", {link.get("href") for link in probe.links}
        )
        self.assertTrue(
            any(href.startswith("/static/style.css") for href in probe.stylesheets)
        )
        self.assert_local_images(probe, {"/static/images/gaman-ridge-runner.jpg"})
        self.assertNotIn("theme-toggle", probe.elements_by_id)
        self.assertNotIn("/static/theme.js", probe.scripts)


if __name__ == "__main__":
    unittest.main()
