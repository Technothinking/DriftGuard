import matplotlib.pyplot as plt
import seaborn as sns

def plot_distribution(ref, curr, feature):
    plt.figure()
    sns.kdeplot(ref, label="Reference")
    sns.kdeplot(curr, label="Current")
    plt.title(f"{feature} Distribution Drift")
    plt.legend()
    plt.show()