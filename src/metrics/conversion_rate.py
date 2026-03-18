def calculate_conversion_rate(df, target_col="deposit"):
    return df[target_col].value_counts(normalize=True).get("yes", 0)