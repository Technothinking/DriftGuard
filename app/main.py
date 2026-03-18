import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd

from src.data.preprocess import preprocess_data
from src.metrics.conversion_rate import calculate_conversion_rate
from src.drift.psi import calculate_psi
from src.drift.statistical_tests import ks_test, chi_square_test
from src.drift.drift_score import compute_drift_score
from src.utils.alerts import generate_alerts
from src.drift.root_cause import get_top_drift_features

st.set_page_config(page_title="DriftGuard", layout="wide")

st.title("📊 DriftGuard Dashboard")

ref_file = st.file_uploader("Upload Reference Data", type="csv")
curr_file = st.file_uploader("Upload Current Data", type="csv")

if ref_file and curr_file:

    ref = pd.read_csv(ref_file)
    curr = pd.read_csv(curr_file)

    ref = preprocess_data(ref)
    curr = preprocess_data(curr)

    # ================= KPI =================
    ref_cr = calculate_conversion_rate(ref)
    curr_cr = calculate_conversion_rate(curr)

    st.subheader("📈 Conversion Rate")
    col1, col2 = st.columns(2)
    col1.metric("Reference", round(ref_cr, 4))
    col2.metric("Current", round(curr_cr, 4))

    # ================= DRIFT =================
    drift_results = {}

    for col in ref.columns:
        if col == "deposit":
            continue

        if ref[col].dtype in ["int64", "float64"]:
            psi = calculate_psi(ref[col], curr[col])
            ks_stat, p_value = ks_test(ref[col], curr[col])

            drift_results[col] = {
                "type": "numeric",
                "psi": round(float(psi), 4),
                "p_value": round(p_value, 4),
                "drift": bool(psi > 0.2 or p_value < 0.05)
            }
        else:
            stat, p_value = chi_square_test(ref[col], curr[col])

            drift_results[col] = {
                "type": "categorical",
                "psi": None,
                "p_value": round(p_value, 4),
                "drift": bool(p_value < 0.05)
            }

    # ================= DRIFT SCORE =================
    drift_score = compute_drift_score(drift_results)

    st.subheader("📊 Drift Score")
    st.metric("Score", f"{drift_score['score']} ({drift_score['level']})")

    # ================= ALERTS =================
    alerts = generate_alerts(ref_cr, curr_cr, drift_score, drift_results)

    st.subheader("🚨 Alerts")
    for alert in alerts:
        st.warning(alert)

    # ================= ROOT CAUSE =================
    top_features = get_top_drift_features(drift_results)

    st.subheader("🔥 Top Drift Drivers")
    for f, s in top_features:
        st.write(f"**{f}** → impact: {round(s, 4)}")

    # ================= TABLE =================
    st.subheader("📋 Feature Drift Table")

    df_results = pd.DataFrame(drift_results).T
    st.dataframe(df_results.style.applymap(
        lambda x: "background-color: red" if x == True else "", subset=["drift"]
    ))

    st.success("✅ Analysis Complete")