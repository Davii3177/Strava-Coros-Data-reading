# Strava-Coros-Data-reading

Pull your run data from Strava and Coros, analyze it with rule-based training logic, and get structured feedback plus tailored workouts — no black-box AI, just transparent metrics and thresholds a coach would actually use.

## Status

🚧 Early stage — project structure and core modules are still being built out.

## Goals

- **Data extraction**: Fetch activity data from the Strava API and Coros API (pace, heart rate, cadence, elevation, splits, etc.), so all your runs live in one place regardless of which device/app recorded them.
- **Analysis**: Apply rule-based logic (pace zones, training load, heart rate drift, splits consistency, weekly mileage trends) to evaluate each run and spot patterns over time.
- **Feedback**: Generate professional-style feedback on individual runs and overall training trends — strengths, red flags (overtraining, pace inconsistency, etc.), and what to focus on next.
- **Workout generation**: Produce tailored upcoming workouts (easy runs, tempo, intervals, long runs) based on recent training load and goals.

## Planned stack

- **Language**: Python
- **Data sources**: Strava API, Coros API (OAuth-based authentication for both)
- **Analysis**: Custom rule-based engine (no external LLM dependency)

## Setup

_Coming soon — will include Strava/Coros API credential setup and installation steps once the initial implementation lands._

## Roadmap

- [ ] Strava API auth + activity fetch
- [ ] Coros API auth + activity fetch
- [ ] Unified data model for runs across both sources
- [ ] Rule-based run analysis engine
- [ ] Feedback report generation
- [ ] Workout plan generation