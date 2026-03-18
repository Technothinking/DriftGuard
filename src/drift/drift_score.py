def compute_drift_score(drift_results):
    total = len(drift_results)
    drifted = sum(1 for v in drift_results.values() if v["drift"])

    score = drifted / total

    if score < 0.2:
        level = "LOW"
    elif score < 0.5:
        level = "MEDIUM"
    else:
        level = "HIGH"

    return {
        "score": round(score, 2),
        "level": level,
        "drifted_features": drifted,
        "total_features": total
    }