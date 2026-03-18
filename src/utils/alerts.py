def generate_alerts(ref_cr, curr_cr, drift_score, drift_results):
    alerts = []

    # KPI Alert
    change = curr_cr - ref_cr
    if abs(change) > 0.05:
        alerts.append(f"⚠️ Conversion rate changed by {round(change, 3)}")

    # Drift Score Alert
    if drift_score["level"] == "HIGH":
        alerts.append("🚨 High overall data drift detected")

    # Feature Drift Alert
    drifted_features = [k for k, v in drift_results.items() if v["drift"]]
    if len(drifted_features) > 5:
        alerts.append(f"⚠️ {len(drifted_features)} features are drifting")

    return alerts