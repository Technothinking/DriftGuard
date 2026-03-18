def get_top_drift_features(drift_results, top_n=3):
    ranked = []

    for feature, res in drift_results.items():
        score = res.get("psi", 0) if res["type"] == "numeric" else (1 - res["p_value"])
        ranked.append((feature, score))

    ranked.sort(key=lambda x: x[1], reverse=True)

    return ranked[:top_n]