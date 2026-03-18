import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

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
    st.dataframe(
        df_results.style.map(
            lambda x: "background-color: red" if x == True else ""
        )
    )

    st.subheader("📊 Drift Score Gauge")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=drift_score["score"] * 100,
        title={"text": "Drift Risk (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"thickness": 0.3},
            "steps": [
                {"range": [0, 20], "color": "green"},
                {"range": [20, 50], "color": "yellow"},
                {"range": [50, 100], "color": "red"},
            ],
        }
    ))

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📉 Feature Distribution Comparison")
    st.info("💡 Tip: Select different features to visually inspect drift patterns")
    selected_feature = st.selectbox("Select Feature", ref.columns)

    if ref[selected_feature].dtype in ["int64", "float64"]:
        fig = px.histogram(
            x=ref[selected_feature],
            nbins=30,
            opacity=0.5,
            title=f"{selected_feature} Distribution (Reference vs Current)"
        )

        fig.add_histogram(x=curr[selected_feature])

        fig.update_layout(barmode='overlay')

    else:
        ref_counts = ref[selected_feature].value_counts(normalize=True)
        curr_counts = curr[selected_feature].value_counts(normalize=True)

        df_plot = pd.DataFrame({
            "Category": list(set(ref_counts.index).union(curr_counts.index)),
            "Reference": [ref_counts.get(x, 0) for x in set(ref_counts.index).union(curr_counts.index)],
            "Current": [curr_counts.get(x, 0) for x in set(ref_counts.index).union(curr_counts.index)],
        })

        fig = px.bar(df_plot, x="Category", y=["Reference", "Current"], barmode="group")

    st.plotly_chart(fig, use_container_width=True)


    st.subheader("📊 Top Drift Features")

    top_df = pd.DataFrame(top_features, columns=["Feature", "Impact"])

    fig = px.bar(
        top_df,
        x="Feature",
        y="Impact",
        title="Top Drift Drivers",
        text="Impact"
    )

    st.plotly_chart(fig, use_container_width=True)


    st.success("✅ Analysis Complete")