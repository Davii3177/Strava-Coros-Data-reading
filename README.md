# Gaman AI

Gaman AI is a password-protected running intelligence dashboard that brings Strava and Coros activity data into one focused experience. It combines transparent training analysis, adaptive workout suggestions, race planning, subjective run feedback, and educational recovery check-ins.

## Live app

**[strava-coros-data-reading.onrender.com](https://strava-coros-data-reading.onrender.com/)**

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
- Responsive light and dark themes

## New Gaman AI experience

The interface was redesigned and renamed from **Run Coach** to **Gaman AI**.

- The startup page now explains how Strava and Coros activities become training analysis, workout suggestions, and recovery guidance.
- The password form is integrated into the hero instead of appearing as a separate login panel.
- GitHub and contact links are available in the startup-page footer.
- Light mode uses an icy white, blue, and yellow palette.
- Dark mode uses black, green, red, and purple.
- The sun/moon control switches themes and includes accessible labels.
- The dashboard includes responsive navigation, glass panels, animated data visuals, clearer metrics, improved tables, and mobile layouts.

## Body & Recovery

The Body & Recovery panel provides an interactive front-and-back anatomy selector with more than 30 detailed regions, including:

- head, jaw, neck, collarbones, shoulders, arms, elbows, forearms, wrists, and hands
- chest, ribs, abdomen, upper/mid/lower back, sacrum, and SI joint
- hips, hip flexors, glutes, groin, adductors, quads, hamstrings, and outer thighs
- kneecap, inner/outer knee, shins, calves, Achilles, ankles, heels, feet, arches, and toes

Users can select multiple regions, specify left/right/both/center, add an exact-location note, rate pain from 1-10, describe sensations and triggers, and save the check-in. Recent distance, elevation, pace, and training-load changes are added as context.

### Recovery safety

Gaman AI provides educational information, not a diagnosis or medical treatment. It does not replace a clinician, physical therapist, athletic trainer, or emergency service.

Red-flag answers such as chest pain, breathing trouble, severe pain, new numbness or weakness, deformity, or inability to bear weight bypass ordinary guidance and display an urgent in-person care recommendation.

The recovery endpoint includes:

- authenticated server-side access
- validated regions, symptom fields, pain levels, and side selection
- a five-request-per-hour session rate limit
- conservative built-in guidance when no AI service is configured
- graceful fallback if the optional AI request fails
- server-side API keys only

Check-ins are stored locally in `data/recovery_checkins.json`.

## Technology

- Python
- Flask and Jinja templates
- Plotly charts
- Strava API integration
- Coros client scaffold with sample-data fallback
- scikit-learn workout model
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

3. Set a required password:

   ```env
   APP_PASSWORD=choose-a-strong-password
   ```

4. Start the application:

   ```bash
   cd src
   python app.py
   ```

The default local address is `http://127.0.0.1:8502/`. When neither Strava nor Coros is connected, Gaman AI uses clearly labeled sample activities so the dashboard remains usable. Sample activities are never mixed into a connected user's real metrics.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `APP_PASSWORD` | Yes | Protects access to the dashboard |
| `FLASK_SECRET_KEY` | Recommended | Provides a persistent Flask session-signing key |
| `STRAVA_CLIENT_ID` | No | Strava application client ID |
| `STRAVA_CLIENT_SECRET` | No | Strava application client secret |
| `STRAVA_REFRESH_TOKEN` | No | Refresh token with activity access |
| `COROS_CLIENT_ID` | No | Reserved for Coros integration |
| `COROS_CLIENT_SECRET` | No | Reserved for Coros integration |
| `OPENAI_API_KEY` | No | Enables optional AI-expanded recovery education |
| `OPENAI_MODEL` | No | Selects the optional server-side model; defaults to `gpt-4o-mini` |
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

## Tests

From the repository root:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
node --check src/static/theme.js
node --check src/static/recovery.js
```

The recovery tests cover ordinary guidance, red-flag escalation, validation, and JSON persistence.

## Deployment notes

The included `render.yaml` can deploy the Flask app to Render. Configure `APP_PASSWORD` and any API credentials in the Render environment settings.

Render's free filesystem is ephemeral. Saved races, workout feedback, and recovery check-ins in `data/*.json` may reset after redeployment or service replacement. The free service can also take roughly 30-60 seconds to wake after inactivity.

### Current data limitations

The unified activity model currently includes date, source, distance, duration, average heart rate, average pace, and elevation gain. Split-level pace, cadence, HRV, resting heart rate, sleep, and detailed elevation streams are shown as unavailable until their source integrations provide them. Gaman AI does not fabricate these fields. Coros production authentication remains a roadmap item, and the current Coros client uses sample activities.

## Project status

- [x] Gaman AI responsive dashboard and startup experience
- [x] Strava authorization and activity fetching
- [x] Rule-based training analysis and workout generation
- [x] Feedback-trained workout adjustment
- [x] Race calendar and tapering logic
- [x] Detailed Body & Recovery check-ins
- [x] Optional AI-expanded recovery education
- [x] Render deployment configuration
- [ ] Production Coros API authentication and activity fetching
- [ ] Durable production database storage

## Contact

- GitHub: [Davii3177/Strava-Coros-Data-reading](https://github.com/Davii3177/Strava-Coros-Data-reading)
- Email: [davidch3@andrew.cmu.edu](mailto:davidch3@andrew.cmu.edu)
