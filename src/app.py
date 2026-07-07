import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

import analysis
import coros_client
import strava_client

load_dotenv()

st.set_page_config(page_title="Run Coach", page_icon="🏃", layout="wide")

st.title("🏃 Run Coach")
st.caption("Data pulled from Strava & Coros, analyzed with rule-based training logic.")

with st.sidebar:
    st.header("Connections")
    st.write("✅ Strava connected" if strava_client.is_configured() else "⚠️ Strava not connected — showing sample data")
    st.write("✅ Coros connected" if coros_client.is_configured() else "⚠️ Coros not connected — showing sample data")
    st.caption("Add API credentials to a `.env` file (see `.env.example`) to connect real accounts.")

runs = strava_client.fetch_runs() + coros_client.fetch_runs()
runs.sort(key=lambda r: r.date, reverse=True)

if not runs:
    st.info("No runs found yet.")
    st.stop()

df = pd.DataFrame(
    [
        {
            "Date": r.date,
            "Source": r.source,
            "Distance (km)": r.distance_km,
            "Duration (min)": r.duration_min,
            "Avg HR": r.avg_hr,
            "Pace": r.pace_str,
            "Pace (min/km)": r.avg_pace_min_km,
            "Elevation (m)": r.elevation_gain_m,
        }
        for r in runs
    ]
)

col1, col2, col3 = st.columns(3)
col1.metric("Total distance", f"{analysis.weekly_mileage_km(runs)} km")
col2.metric("Avg pace", f"{analysis.avg_pace_min_km(runs)} min/km")
col3.metric("Runs", len(runs))

st.subheader("Recent runs")
st.dataframe(df.drop(columns=["Pace (min/km)"]), use_container_width=True, hide_index=True)

st.subheader("Pace trend")
fig = px.line(df.sort_values("Date"), x="Date", y="Pace (min/km)", markers=True, color="Source")
fig.update_yaxes(autorange="reversed")  # lower pace value = faster
st.plotly_chart(fig, use_container_width=True)

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📋 Feedback")
    for line in analysis.generate_feedback(runs):
        st.write(f"- {line}")

with col_b:
    st.subheader("🎯 Suggested next workouts")
    for line in analysis.generate_next_workouts(runs):
        st.write(f"- {line}")
