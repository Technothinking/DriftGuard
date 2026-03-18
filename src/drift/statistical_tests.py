from scipy.stats import ks_2samp, chi2_contingency

def ks_test(ref, curr):
    stat, p_value = ks_2samp(ref, curr)
    return stat, p_value


def chi_square_test(ref_col, curr_col):
    ref_counts = ref_col.value_counts()
    curr_counts = curr_col.value_counts()

    all_categories = set(ref_counts.index).union(set(curr_counts.index))

    ref_freq = [ref_counts.get(cat, 0) for cat in all_categories]
    curr_freq = [curr_counts.get(cat, 0) for cat in all_categories]

    contingency = [ref_freq, curr_freq]

    stat, p_value, _, _ = chi2_contingency(contingency)

    return stat, p_value