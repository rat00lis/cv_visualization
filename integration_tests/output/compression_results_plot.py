import json
import os
import matplotlib.pyplot as plt

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "compression_results.json")
OUTPUT_IMAGE = os.path.join(os.path.dirname(__file__), "compressed_results_plot.png")

def plot_results():
    if not os.path.exists(RESULTS_FILE):
        print("No results found.")
        return

    with open(RESULTS_FILE, 'r') as f:
        results = json.load(f)

    if not results:
        print("Results file is empty.")
        return

    results = [r for r in results if r.get("success") and r.get("original_size")]

    # Sort by compressed size
    results.sort(key=lambda x: x["size_bytes"])

    names = [r["name"] for r in results]
    sizes = [r["size_bytes"] for r in results]
    original_sizes = [r["original_size"] for r in results]
    percentages = [(s / o) * 100 for s, o in zip(sizes, original_sizes)]

    # Get the 100% reference line (original vector size)
    baseline_percentages = [100.0 for _ in results]

    plt.figure(figsize=(12, 6))
    bars = plt.bar(names, percentages, label="Compressed Size (% of Original)")

    # Draw a red horizontal line at 100% for each bar (baseline)
    for i, baseline in enumerate(baseline_percentages):
        x_center = bars[i].get_x() + bars[i].get_width() / 2
        plt.plot([x_center - 0.2, x_center + 0.2], [baseline, baseline], color="red", linewidth=2)

    plt.xlabel("Compression Method")
    plt.ylabel("Size (% of original)")
    plt.title("Compression Efficiency of Different Methods")
    plt.ylim(0, max(percentages + [100]) + 20)

    # Annotate bars with actual byte sizes
    for bar, size in zip(bars, sizes):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                 f"{size:,} B", ha='center', fontsize=8)

    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE)
    print(f"Saved plot to {OUTPUT_IMAGE}")

if __name__ == "__main__":
    plot_results()
