"""
============================================================
  utils/chart_generator.py
  Generates Matplotlib charts as base64 PNG strings
  for embedding directly in Jinja2 templates.
============================================================
"""

import matplotlib
matplotlib.use("Agg")          # Non-interactive backend (no display needed)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import MaxNLocator
import base64
import io


# ── Palette ────────────────────────────────────────────────────────────────
COLORS = {
    "POSITIVE": "#22c55e",   # emerald green
    "NEGATIVE": "#ef4444",   # rose red
    "NEUTRAL":  "#94a3b8",   # slate gray
}
BG_COLOR   = "#0f172a"       # dark navy background (matches UI)
TEXT_COLOR = "#e2e8f0"       # light text


def _fig_to_base64(fig) -> str:
    """Convert a matplotlib Figure to a base64 PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight",
                facecolor=BG_COLOR, dpi=130)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return img_b64


def generate_pie_chart(label_counts: dict) -> str:
    """
    Generate a donut-style pie chart for sentiment distribution.

    Args:
        label_counts (dict): { "POSITIVE": int, "NEGATIVE": int, "NEUTRAL": int }

    Returns:
        str: base64-encoded PNG image.
    """
    labels = [k for k, v in label_counts.items() if v > 0]
    sizes  = [label_counts[k] for k in labels]
    colors = [COLORS.get(k, "#6366f1") for k in labels]

    fig, ax = plt.subplots(figsize=(5, 4), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    if not any(sizes):
        ax.text(0.5, 0.5, "No data yet", ha="center", va="center",
                color=TEXT_COLOR, fontsize=14, transform=ax.transAxes)
        ax.axis("off")
        return _fig_to_base64(fig)

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels      = None,
        colors      = colors,
        autopct     = "%1.1f%%",
        startangle  = 140,
        pctdistance = 0.75,
        wedgeprops  = dict(width=0.55, edgecolor=BG_COLOR, linewidth=2),
    )
    for at in autotexts:
        at.set_color(TEXT_COLOR)
        at.set_fontsize(11)
        at.set_fontweight("bold")

    # Legend
    legend_patches = [
        mpatches.Patch(color=COLORS.get(lbl, "#6366f1"), label=f"{lbl}  ({label_counts.get(lbl,0)})")
        for lbl in ["POSITIVE", "NEGATIVE", "NEUTRAL"]
    ]
    ax.legend(handles=legend_patches, loc="lower center",
              bbox_to_anchor=(0.5, -0.12), ncol=3,
              frameon=False, fontsize=9, labelcolor=TEXT_COLOR)

    ax.set_title("Sentiment Distribution", color=TEXT_COLOR,
                 fontsize=13, fontweight="bold", pad=12)
    return _fig_to_base64(fig)


def generate_bar_chart(daily_counts: list) -> str:
    """
    Generate a bar chart of daily analysis volume (last 7 days).

    Args:
        daily_counts (list): [{ "date": "YYYY-MM-DD", "count": int }, ...]

    Returns:
        str: base64-encoded PNG image.
    """
    fig, ax = plt.subplots(figsize=(6.5, 4), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    if not daily_counts:
        ax.text(0.5, 0.5, "No data yet", ha="center", va="center",
                color=TEXT_COLOR, fontsize=14, transform=ax.transAxes)
        ax.axis("off")
        return _fig_to_base64(fig)

    # Use last 7 entries
    recent = daily_counts[-7:]
    dates  = [d["date"][5:] for d in recent]   # strip year → "MM-DD"
    counts = [d["count"] for d in recent]

    # Gradient-ish bars with gradient fill via iteration
    bar_colors = ["#6366f1", "#818cf8", "#a5b4fc", "#c7d2fe",
                  "#818cf8", "#6366f1", "#4f46e5"]
    bars = ax.bar(dates, counts, color=bar_colors[:len(dates)],
                  width=0.55, edgecolor="none", zorder=3)

    # Value labels on top of bars
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.15,
                str(count),
                ha="center", va="bottom",
                color=TEXT_COLOR, fontsize=10, fontweight="bold")

    # Styling
    ax.set_title("Daily Analyses (Last 7 Days)", color=TEXT_COLOR,
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Date", color=TEXT_COLOR, fontsize=10, labelpad=8)
    ax.set_ylabel("Count", color=TEXT_COLOR, fontsize=10, labelpad=8)
    ax.tick_params(colors=TEXT_COLOR, labelsize=9)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="y", color="#1e293b", linewidth=0.8, zorder=0)
    ax.set_ylim(0, max(counts) * 1.25 if counts else 1)

    return _fig_to_base64(fig)
