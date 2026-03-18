from src.utils.config import load_config
from src.data.load_data import load_data
from src.data.preprocess import preprocess_data
from src.metrics.conversion_rate import calculate_conversion_rate
from src.drift.psi import calculate_psi
from src.utils.logger import get_logger
from src.drift.statistical_tests import ks_test, chi_square_test
from src.drift.drift_report import generate_html_report
from src.drift.drift_score import compute_drift_score
from src.utils.alerts import generate_alerts
from src.drift.root_cause import get_top_drift_features

logger = get_logger()

def main():
    config = load_config()

    # Load data
    ref = load_data(config["data"]["reference_path"])
    curr = load_data(config["data"]["current_path"])

    # Preprocess
    ref = preprocess_data(ref)
    curr = preprocess_data(curr)

    # KPI check
    ref_cr = calculate_conversion_rate(ref)
    curr_cr = calculate_conversion_rate(curr)

    logger.info(f"Reference Conversion Rate: {ref_cr}")
    logger.info(f"Current Conversion Rate: {curr_cr}")

    # Drift detection (numeric only for now)
    drift_results = {}

    for col in ref.columns:
        
        if col == config["target_column"]:
            continue

        # NUMERIC FEATURES
        if ref[col].dtype in ["int64", "float64"]:
            psi = calculate_psi(ref[col], curr[col])
            ks_stat, p_value = ks_test(ref[col], curr[col])

            drift_results[col] = {
                "type": "numeric",
                "psi": round(float(psi), 4),
                "p_value": round(p_value, 4),
                "drift": bool(
                    psi > config["drift"]["psi_threshold"] or
                    p_value < config["drift"]["significance_level"]
                )
            }

        # CATEGORICAL FEATURES
        else:
            stat, p_value = chi_square_test(ref[col], curr[col])

            drift_results[col] = {
                "type": "categorical",
                "p_value": round(p_value, 4),
                "drift": bool(p_value < config["drift"]["significance_level"])
            }

    print("\n===== DRIFT SUMMARY =====\n")

    for feature, res in drift_results.items():
        print(f"{feature} ({res['type']}) → Drift: {res['drift']}")


    generate_html_report(
    drift_results,
    drift_score,
    alerts,
    top_features,
    config["output"]["report_path"]
    )

    logger.info("HTML Drift Report Generated ✅")

    drift_score = compute_drift_score(drift_results)

    print("\n===== DRIFT SCORE =====")
    print(drift_score)  

    alerts = generate_alerts(ref_cr, curr_cr, drift_score, drift_results)

    print("\n===== ALERTS =====")
    for alert in alerts:
        print(alert)
    
    top_features = get_top_drift_features(drift_results)

    print("\n===== TOP DRIFT DRIVERS =====")
    for f, s in top_features:
        print(f"{f} → impact score: {round(s, 4)}")


if __name__ == "__main__":
    main()