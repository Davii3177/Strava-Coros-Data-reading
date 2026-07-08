# Strava-Coros-Data-reading

Pull your run data from Strava and Coros, analyze it with rule-based training logic, and get structured feedback plus tailored workouts — no black-box AI, just transparent metrics and thresholds a coach would actually use.

## Status

🚧 In progress — dashboard is live with real Strava activity data; Coros integration is next.

## Goals

- **Data extraction**: Fetch activity data from the Strava API and Coros API (pace, heart rate, cadence, elevation, splits, etc.), so all your runs live in one place regardless of which device/app recorded them.
- **Analysis**: Apply rule-based logic (pace zones, training load, heart rate drift, splits consistency, weekly mileage trends) to evaluate each run and spot patterns over time.
- **Feedback**: Generate professional-style feedback on individual runs and overall training trends — strengths, red flags (overtraining, pace inconsistency, etc.), and what to focus on next.
- **Workout generation**: Produce tailored upcoming workouts (easy runs, tempo, intervals, long runs) based on recent training load and goals.

## Stack

- **Language**: Python
- **Dashboard**: Streamlit
- **Data sources**: Strava API, Coros API (OAuth-based authentication for both)
- **Analysis**: Custom rule-based engine (no external LLM dependency)

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in Strava/Coros credentials once you have them
cd src
streamlit run app.py
```

Without credentials in `.env`, the dashboard runs on sample data so you can see it working end to end.

### Connecting Strava

1. Register an app at [strava.com/settings/api](https://www.strava.com/settings/api) and set **Authorization Callback Domain** to `localhost`.
2. Add the app's Client ID and Client Secret to `.env` (`STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`).
3. Run the local OAuth helper and open the page it prints:
   ```bash
   cd src
   python strava_auth_server.py
   ```
4. Click **Connect with Strava**, authorize with activity read access, and it writes `STRAVA_REFRESH_TOKEN` into `.env` for you automatically.

### Connecting Coros

Not yet implemented — `coros_client.py` still returns sample data.

## Roadmap

- [x] Dashboard scaffold (Streamlit) with sample data
- [x] Rule-based feedback and workout generation logic
- [x] Strava API auth + activity fetch
- [ ] Coros API auth + activity fetch
- [ ] Unified data model for runs across both sources
- [ ] Deploy dashboard (Streamlit Community Cloud or similar)