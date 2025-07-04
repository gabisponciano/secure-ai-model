import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# File paths
csv_dev = "results/benchmark.csv"
csv_prod = "dist_protected/results/benchmark.csv"

# Output directory
output_dir = Path("results_comparison")
output_dir.mkdir(exist_ok=True)

# Load data
df_dev = pd.read_csv(csv_dev)
df_prod = pd.read_csv(csv_prod)

# Benchmark metrics
metrics = ["decryption_time", "load_time", "inference_time", "total_time"]

# Rolling average window
rolling_window = 250

# Comparison and plotting
for metric in metrics:
    mean_dev = df_dev[metric].mean()
    mean_prod = df_prod[metric].mean()
    std_dev = df_dev[metric].std()
    std_prod = df_prod[metric].std()

    diff_abs = mean_prod - mean_dev
    diff_pct = (diff_abs / mean_dev) * 100 if mean_dev != 0 else 0

    # Performance interpretation
    if diff_abs > 0:
        trend = f"X Slower (+{diff_abs:.6f}s, {diff_pct:.2f}%)"
        arrow = "↑"
    elif diff_abs < 0:
        trend = f"✔ Faster ({diff_abs:.6f}s, {diff_pct:.2f}%)"
        arrow = "↓"
    else:
        trend = "No difference"
        arrow = "→"

    # Console output
    print(f"\n🔹 {metric.replace('_', ' ').title()}")
    print(f"  Dev:  Mean = {mean_dev:.6f}s | Std = {std_dev:.6f}")
    print(f"  Prod: Mean = {mean_prod:.6f}s | Std = {std_prod:.6f}")
    print(f"  ➤ {arrow} {trend}")

    # Rolling averages
    dev_smooth = df_dev[metric].rolling(rolling_window).mean()
    prod_smooth = df_prod[metric].rolling(rolling_window).mean()

    # Plot
    plt.figure(figsize=(10, 5))
    plt.plot(dev_smooth, label=f"Dev (rolling {rolling_window})", color='blue', alpha=0.7)
    plt.plot(prod_smooth, label=f"Prod (rolling {rolling_window})", color='orange', alpha=0.7)

    plt.axhline(mean_dev, color='blue', linestyle='--', alpha=0.4, label=f"Dev mean: {mean_dev:.4f}s")
    plt.axhline(mean_prod, color='orange', linestyle='--', alpha=0.4, label=f"Prod mean: {mean_prod:.4f}s")

    plt.title(f"{metric.replace('_', ' ').title()} — {trend}")
    plt.xlabel("Run")
    plt.ylabel("Time (s)")
    plt.legend()
    plt.tight_layout()

    output_file = output_dir / f"comparison_{metric}.png"
    plt.savefig(output_file)
    plt.close()

print(f"\n✅ Plots and comparison saved in: {output_dir.absolute()}")
