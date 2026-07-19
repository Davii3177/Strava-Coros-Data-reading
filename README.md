# Gaman

Gaman is a password-protected running dashboard that brings Strava and Coros activity data into one focused experience. It combines transparent training analysis, adaptive workout suggestions, race planning, subjective run feedback, and educational recovery check-ins.

## Live app

**[www.gamanrun.com](https://www.gamanrun.com/)**

The hosted app is password-protected. Ask the owner for access.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Davii3177/Strava-Coros-Data-reading)

## Current features

- A prominent **Today's Run** prescription with distance, duration, target, warm-up, cool-down, recovery time, purpose, and a transparent “Why this?” explanation
- Workout completion states for completed, shortened, modified, or skipped sessions
- A transparent readiness status comparing the last seven days with the previous four-week weekly average
- A plan-versus-actual weekly view with missed-session and consecutive-hard-day adjustments
- Individual run-analysis pages that use available summary data and explicitly label missing splits, cadence, HR drift, and grade-adjusted pace
- A priority race center with training phase, countdown, target pace, an explainable finish range, pacing guidance, and checklist
- Shoe inventory, activity assignment, mileage, retirement, replacement-distance progress, and observed pace/soreness associations
- Recovery symptom trends, guidance-adherence tracking, and an exportable clinician-friendly text summary
- Calculated personal records and consistency streaks with estimated/official distinctions
- Unified recent activity view for Strava and Coros data
- Weekly distance, average pace, heart rate, elevation, and pace-trend visualization
- Rule-based coaching feedback and seven-day workout suggestions
- Training calendar with automatic pre-race tapering
- Race-day planning and saved race goals
- Per-run difficulty, soreness, motivation, and notes
- A trained workout model that adapts suggestions from logged feedback
- Detailed Body & Recovery check-ins with saved history
- Optional server-side AI-expanded recovery education
- **Ask Gaman**, an optional Gemini-powered chat assistant that answers training questions grounded in your logged runs, readiness, and races
- A **research library** at `/research`: a source-cited, evidence-graded review of 110 peer-reviewed papers on running-related pain by body region, with region-matched citations shown alongside recovery check-in guidance
- A consistent responsive light theme

## Editorial trail-running experience

The interface was redesigned and renamed from **Run Coach** to **Gaman**.

- The authenticated product is organized into five focused areas: **Overview**, **Training**, **Activities**, **Body & Recovery**, and **Profile**. Every previous tool remains available, but unrelated workflows no longer compete on one long page.
- **Overview** prioritizes Today's Run, readiness, weekly mileage, and the recommendation evidence. **Training** contains the weekly plan, race goal, records, calendar, pace trend, suggested sessions, and race management.
- **Activities** contains searchable run details, the complete activity table, saved feedback, dismissal, deletion, and seven-day prompt expiry. **Body & Recovery** owns the anatomy selector, symptom form, guidance, history, adherence, and export. **Profile** contains connection status, shoes, assignments, privacy, and contact information.
- Real running data—including pace, distance, heart rate, elevation, shoes, race countdowns, and recovery trends—provides the visual focus.
- Recommendations use short, specific language and show the data behind the suggestion. Measured facts, estimates, and coaching guidance remain clearly distinguished.
- An intentionally restrained palette uses white and warm-grey surfaces, charcoal text, and a small amount of purple for emphasis, with distinct green, amber, and red status colors so success, caution, and danger states are readable at a glance.
- Typography pairs two self-hosted webfonts (no third-party CDN): **Instrument Serif** for editorial display headings and **Geist** for body copy, controls, and tabular metrics. The `woff2` files live under `src/static/fonts/`.
- Original cinematic trail-running imagery gives the product a distinctive identity without distracting from the data.
- The responsive light theme retains readable contrast, keyboard focus styles, reduced-motion support, and clear status colors.
- Consistent spacing, borders, and icons keep the expressive visual language practical. Motion is limited to useful feedback such as loading, progress, and state changes.
- Desktop navigation uses a stable product sidebar. Mobile navigation uses a compact five-destination bottom bar with a visible active state.
- Search, compact views, and collapsible sections keep detailed tools available without overwhelming the main dashboard. Activity Details shows four runs and Run Feedback shows three prompts by default; both support search and Show all/less controls, while feedback deletion, dismissal, and seven-day prompt expiry remain intact.
- The landing page uses a concise white header and full-bleed cinematic imagery, with one headline, one supporting sentence, and a single Open Dashboard button that reveals a compact password dialog.
- The landing page contains one concise hero, a "real Tuesday" narrative section paired with a live-styled product preview card (instead of generic numbered feature tiles), a short workflow preview, safety boundaries, a detailed About section, and a footer. The complete technical explanation now lives at `/how-it-works`.
- The authenticated product shares one editorial system: white and warm-gray surfaces, charcoal text, restrained purple interaction states, consistent cards, Geist controls, and Instrument Serif for major page titles.
- Landing, About, dashboard, run-detail, and recovery interfaces share the same responsive light system, visible keyboard focus, and reduced-motion behavior.

### Image assets and visual direction

The following project-local assets are original images generated for Gaman using the built-in OpenAI image generation workflow. They are stored under `src/static/images`:

- `gaman-mountain-road-hero.jpg`
- `gaman-mountain-valley.jpg`
- `gaman-ridge-runner.jpg`
- `gaman-0716-poster.jpg` (poster extracted from the owner-supplied hero video)

### Hero video

The owner-supplied hero footage is served at full length (33 seconds), re-encoded for web playback, as:

- `src/static/videos/gaman-0716-hero-compressed.mp4` (1080p, 30fps, H.264 ~3.3 Mbps, no audio track — the original 70 MB source is downsampled to keep the autoplay/loop background video from bogging down playback the longer a visitor stays on the page)

The poster (`gaman-0716-poster-v2.jpg`) is used for reduced-motion preferences, small screens, and data-saver connections. The video file is local, so the homepage has no third-party media dependency.

[WallpaperSafari's Vintage Aesthetic Landscape collection](https://wallpapersafari.com/vintage-aesthetic-landscape-wallpapers/) was used only as visual direction. No WallpaperSafari-hosted image is integrated into the project because its [copyright policy](https://wallpapersafari.com/page/copyright-policy/) requires permission from the relevant creator and its [terms of service](https://wallpapersafari.com/page/terms-of-service/) prohibit integrating hosted files without express written permission.

## Body & Recovery

The Body & Recovery panel provides an interactive front-and-back anatomy selector with more than 30 detailed regions, including:

- head, jaw, neck, collarbones, shoulders, arms, elbows, forearms, wrists, and hands
- chest, ribs, abdomen, upper/mid/lower back, sacrum, and SI joint
- hips, hip flexors, glutes, groin, adductors, quads, hamstrings, and outer thighs
- kneecap, inner/outer knee, shins, calves, Achilles, ankles, heels, feet, arches, and toes

Users can select multiple regions, specify left/right/both/center, add an exact-location note, rate pain from 1-10, describe sensations and triggers, and save the check-in. Recent distance, elevation, pace, and training-load changes are added as context.

### Recovery safety

Gaman provides educational information, not a diagnosis or medical treatment. It does not replace a clinician, physical therapist, athletic trainer, or emergency service.

Red-flag answers such as chest pain, breathing trouble, severe pain, new numbness or weakness, deformity, or inability to bear weight bypass ordinary guidance and display an urgent in-person care recommendation.

The recovery endpoint includes:

- authenticated server-side access
- validated regions, symptom fields, pain levels, and side selection
- a five-request-per-hour session rate limit
- conservative built-in guidance when no AI service is configured
- graceful fallback if the optional AI request fails
- server-side API keys only

Check-ins are stored locally in `data/recovery_checkins.json`.

Non-urgent check-in results also include **region-matched educational reading**: one to three peer-reviewed references per selected body area, drawn verbatim from the committed literature review (see below), with a deep link into the matching `/research` section. Urgent results omit them so the in-person care message stays the focus.

## Research library

`RESEARCH.md` is a source-cited, evidence-graded literature review of running-related pain and soreness — 110 individually verified peer-reviewed papers organized head-to-toe across 13 body regions, with an evidence-based treatment matrix, practical interpretation, red flags, and limitations. It is served as a styled page at `/research` (regions are deep-linkable as `/research#region-0` through `#region-12`).

The page is generated from `RESEARCH.md` by `tools/build_research_page.py` (run it whenever the document changes; python-markdown is a build-time tool only, not an app dependency). A test verifies that every citation used by the recovery check-in exists verbatim in `RESEARCH.md`, so in-app references can never drift from the source document.

## Ask Gaman (optional chat assistant)

Ask Gaman is a chat assistant available from a compact floating icon launcher on
every authenticated dashboard page. Each question is sent to Google's Gemini API
together with a compact, grounded snapshot of the runner's own data — readiness,
recent runs, weekly load, today's recommended session, an upcoming race, and
recovery trends — so answers reference real numbers rather than generic advice.
Answers are kept short (a one-line recommendation plus a few bullets) and
rendered with basic Markdown (bold, lists) instead of raw formatting characters.

To enable it, set `GEMINI_API_KEY` (and optionally `GEMINI_MODEL`, default
`gemini-flash-lite-latest`) in `.env`. The `POST /api/ask` endpoint:

- requires an authenticated session
- validates and length-caps the question, and keeps only the recent turns of history
- limits requests to twenty per hour per session
- instructs the model to stay conservative, never invent missing metrics, avoid
  diagnosis, and defer injury/medical questions to a clinician and the Body &
  Recovery check-in
- degrades gracefully: with no key it returns a friendly "not set up yet" message,
  and any API error falls back to a safe "try again" response

Data is sent to Google only when a runner actually uses Ask Gaman, and the key is
read only on the server.

## Technology

- Python
- Flask and Jinja templates
- Plotly charts
- Strava API integration
- Fitbit integration via the Google Health API
- Coros client scaffold with sample-data fallback
- Pure-Python trained workout model (in-house ordinary-least-squares fit, no external ML dependency)
- Optional OpenAI and Google Gemini API integrations (recovery education and Ask Gaman)
- JSON-backed local storage
- Vanilla JavaScript and responsive CSS
- Gunicorn and Render deployment

## Local setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create `.env` from `.env.example`:

   ```powershell
   Copy-Item .env.example .env
   ```

3. Set a unique, strong password (never share it in chat, source control, or screenshots):

   ```env
   APP_PASSWORD=choose-a-strong-password
   ```

4. Start the application:

   ```bash
   cd src
   python app.py
   ```

The default local address is `http://127.0.0.1:8502/`. When none of Strava, Coros, or Fitbit is connected, Gaman uses clearly labeled sample activities so the dashboard remains usable. Sample activities are never mixed into a connected user's real metrics.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `APP_PASSWORD` | First setup only | Creates the first account at `/register`; use a long unique value and rotate it afterward |
| `REGISTRATION_CODE` | No | Invitation code for creating additional accounts at `/register` |
| `RUNNER_TIMEZONE` | Recommended | IANA timezone (e.g. `America/New_York`) for the runner's actual location; without it, a deployed server running in UTC (Render and most hosts) rolls "today" over hours before the runner's actual midnight, silently showing tomorrow's workout in the evening |
| `FLASK_SECRET_KEY` | Recommended | Provides a persistent Flask session-signing key |
| `FLASK_COOKIE_SECURE` | Production | Set `true` on HTTPS hosting; keep `false` for local HTTP development |
| `DATABASE_URL` | Production | PostgreSQL connection string; Render supplies it from the Blueprint database |
| `DATABASE_PATH` | Local | SQLite fallback path for local development only |
| `STRAVA_CLIENT_ID` | No | Strava application client ID |
| `STRAVA_CLIENT_SECRET` | No | Strava application client secret |
| `STRAVA_REFRESH_TOKEN` | No | Refresh token with activity access |
| `COROS_CLIENT_ID` | No | Reserved for Coros integration |
| `COROS_CLIENT_SECRET` | No | Reserved for Coros integration |
| `GOOGLE_HEALTH_CLIENT_ID` | No | Google Cloud OAuth 2.0 client ID for Fitbit data via the Google Health API |
| `GOOGLE_HEALTH_CLIENT_SECRET` | No | Google Cloud OAuth 2.0 client secret |
| `GOOGLE_HEALTH_REFRESH_TOKEN` | No | Refresh token with the `googlehealth.activity_and_fitness.readonly` scope |
| `OPENAI_API_KEY` | No | Enables optional AI-expanded recovery education |
| `OPENAI_MODEL` | No | Selects the optional server-side model; defaults to `gpt-4o-mini` |
| `GEMINI_API_KEY` | No | Enables the optional Ask Gaman chat assistant |
| `GEMINI_MODEL` | No | Selects the Ask Gaman model; defaults to `gemini-flash-lite-latest` |
| `PORT` | No | Overrides the local server port |

Never expose API credentials in templates or client-side JavaScript.

## Connecting Strava

1. Register an app at [strava.com/settings/api](https://www.strava.com/settings/api) and set the authorization callback domain to `localhost`.
2. Add `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET` to `.env`.
3. Run the OAuth helper:

   ```bash
   cd src
   python strava_auth_server.py
   ```

4. Open the displayed URL and authorize activity access. The helper writes `STRAVA_REFRESH_TOKEN` to `.env`.

## Connecting Fitbit (Google Health API)

Google is retiring the legacy Fitbit Web API (`dev.fitbit.com`) in **September 2026** and replacing it with the [Google Health API](https://developers.google.com/health/migration), which uses standard Google OAuth 2.0. Gaman targets the new API, so Fitbit connections use **Google Cloud** credentials rather than a `dev.fitbit.com` app.

1. In the [Google Cloud Console](https://console.cloud.google.com/), create (or pick) a project and **enable the Google Health API**.
2. Configure the **OAuth consent screen**: add the scope `https://www.googleapis.com/auth/googlehealth.activity_and_fitness.readonly`, and — while the app is unverified (publishing status "Testing") — add your own Google account under **Test users**.
3. Create an **OAuth 2.0 Client ID** (Application type: **Web application**) and add `http://localhost:8000/callback` to its **Authorized redirect URIs** (Google requires an exact match).
4. Put the client ID and secret into `.env` as `GOOGLE_HEALTH_CLIENT_ID` and `GOOGLE_HEALTH_CLIENT_SECRET`.
5. Run the OAuth helper and sign in with the Google account your Fitbit is linked to:

   ```bash
   cd src
   python fitbit_auth_server.py
   ```

6. Open the displayed URL, authorize activity access, and the helper writes `GOOGLE_HEALTH_REFRESH_TOKEN` to `.env`.

**Two Google-specific gotchas:**

- **Restricted scopes.** The `googlehealth.*` scopes are Restricted. Personal/test use works with the app in "Testing" status and your account added as a test user; publishing to Production (needed for other people, or to stop the token expiring) requires Google's security assessment.
- **7-day refresh token in Testing.** Google expires refresh tokens after ~7 days while an app is in "Testing" status, so you'll re-run the helper weekly until the app is verified/Production. Google refresh tokens do **not** rotate on each use, so no `.env` rewriting happens during normal fetches (unlike the old Fitbit API).

> **Field-mapping note:** Google's public reference does not yet fully document the leaf field names inside an `exercise` data point (distance, duration, heart rate). `src/fitbit_client.py` maps them best-effort and resiliently; if real runs come back with zeros, capture one raw response and tighten the candidate keys in `_to_run` / `_find`.

## Tests

From the repository root:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
node --check src/static/recovery.js
node --check src/static/dashboard_compact.js
node --check src/static/run_panels.js
```

The recovery tests cover ordinary guidance, red-flag escalation, validation, and JSON persistence.

## Deployment notes

The included `render.yaml` provisions the web service and a Render Postgres database for accounts and connection/sync status. Configure `APP_PASSWORD`, `REGISTRATION_CODE`, and API credentials in Render. On first launch, visit `/register` and use `APP_PASSWORD` as the one-time setup code to make the owner account; then rotate or remove it and set `REGISTRATION_CODE` only when inviting another user.

Render's free filesystem is ephemeral. Accounts and connection/sync status use Postgres, but the legacy race, feedback, shoe, plan, and recovery JSON stores still need a final per-user data migration before they are durable and multi-user safe. The free service can also take roughly 30-60 seconds to wake after inactivity.

### Custom domain

`www.gamanrun.com` is configured as a custom domain on the Render service, with DNS managed at the registrar/DNS provider pointing a `CNAME` at the Render hostname. Render auto-verifies the domain and issues a free TLS certificate once DNS resolves correctly.

### Current data limitations

The unified activity model currently includes date, source, distance, duration, average heart rate, average pace, and elevation gain. Split-level pace, cadence, HRV, resting heart rate, sleep, and detailed elevation streams are shown as unavailable until their source integrations provide them. Gaman does not fabricate these fields. Coros production authentication remains a roadmap item, and the current Coros client uses sample activities.

## Project status

- [x] Gaman responsive dashboard and startup experience
- [x] Strava authorization and activity fetching
- [x] Fitbit authorization and activity fetching (Google Health API)
- [x] Rule-based training analysis and workout generation
- [x] Feedback-trained workout adjustment
- [x] Race calendar and tapering logic
- [x] Detailed Body & Recovery check-ins
- [x] Optional AI-expanded recovery education
- [x] Ask Gaman chat assistant (Gemini-powered)
- [x] Render deployment configuration with a custom domain
- [ ] Production Coros API authentication and activity fetching
- [ ] Durable production database storage

## Contact

- GitHub: [Davii3177/Strava-Coros-Data-reading](https://github.com/Davii3177/Strava-Coros-Data-reading)
- Email: [davidch3@andrew.cmu.edu](mailto:davidch3@andrew.cmu.edu)
