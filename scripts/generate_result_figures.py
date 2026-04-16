from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def main() -> None:
    sns.set_theme(style="whitegrid")

    out_dir = Path("outputs/final_ablation")
    fig_dir = out_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    summary = pd.read_csv(out_dir / "ablation_summary.csv")
    all_df = pd.read_csv(out_dir / "ablation_metrics_all.csv")
    pair_df = pd.read_csv(out_dir / "ablation_pairwise_composite.csv")

    # 1) Main method comparison
    plt.figure(figsize=(8, 4.8))
    order = summary.sort_values("composite_score", ascending=False)["method"]
    ax = sns.barplot(
        data=summary,
        x="method",
        y="composite_score",
        hue="method",
        order=order,
        palette="viridis",
        legend=False,
    )
    ax.set_title("Composite Score by Method")
    ax.set_xlabel("Method")
    ax.set_ylabel("Composite Score")
    for p in ax.patches:
        h = p.get_height()
        ax.annotate(f"{h:.3f}", (p.get_x() + p.get_width() / 2, h), ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(fig_dir / "fig1_method_composite.png", dpi=220)
    plt.close()

    # 2) Metric radar-style substitute: grouped bars
    metric_cols = [
        "content_similarity",
        "target_culture_signal",
        "adaptation_depth",
        "lexical_shift",
        "stereotype_risk",
    ]
    melt = summary.melt(id_vars=["method"], value_vars=metric_cols, var_name="metric", value_name="score")
    plt.figure(figsize=(10.5, 5.4))
    ax = sns.barplot(data=melt, x="metric", y="score", hue="method")
    ax.set_title("Metric-wise Comparison Across Methods")
    ax.set_xlabel("Metric")
    ax.set_ylabel("Score")
    ax.tick_params(axis="x", rotation=20)
    plt.tight_layout()
    plt.savefig(fig_dir / "fig2_metricwise_methods.png", dpi=220)
    plt.close()

    # 3) Genre-wise composite by method
    genre = all_df.groupby(["method", "genre"], as_index=False)["composite_score"].mean()
    plt.figure(figsize=(9, 5))
    ax = sns.barplot(data=genre, x="genre", y="composite_score", hue="method")
    ax.set_title("Genre-wise Composite Score")
    ax.set_xlabel("Genre")
    ax.set_ylabel("Composite Score")
    plt.tight_layout()
    plt.savefig(fig_dir / "fig3_genrewise_composite.png", dpi=220)
    plt.close()

    # 4) Pairwise heatmap for best available method
    best_method = summary.sort_values("composite_score", ascending=False).iloc[0]["method"]
    best_df = pair_df[pair_df["method"] == best_method]
    mat = best_df.pivot(index="source_culture", columns="target_culture", values="composite_score")
    plt.figure(figsize=(9, 6.5))
    ax = sns.heatmap(mat, annot=True, fmt=".3f", cmap="YlGnBu", cbar_kws={"label": "Composite"})
    ax.set_title(f"Pairwise Composite ({best_method})")
    ax.set_xlabel("Target culture")
    ax.set_ylabel("Source culture")
    plt.tight_layout()
    plt.savefig(fig_dir / "fig4_pairwise_heatmap_best_method.png", dpi=220)
    plt.close()

    print(f"Saved figures to {fig_dir}")


if __name__ == "__main__":
    main()
