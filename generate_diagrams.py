import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(12, 5.5), facecolor="#0b101b")
    ax.set_facecolor("#0b101b")
    ax.axis("off")

    # Define boxes [x, y, width, height, label, sublabel, border_color]
    boxes = [
        (0.02, 0.35, 0.16, 0.45, "1. Data Pipeline", "M5 Retail (30k SKUs)\nDataCo Supply Chain\nRegime Split (CV > 0.3)", "#38bdf8"),
        (0.22, 0.35, 0.16, 0.45, "2. Base Forecaster", "LightGBM Quantile\nRolling-Origin CV\nMAE Loss Optimization", "#38bdf8"),
        (0.42, 0.35, 0.18, 0.45, "3. ACI Engine", "Gibbs & Candès (2022)\nα_{t+1} = α_t + γ(...)\nDynamic Interval Width", "#00e5ff"),
        (0.64, 0.35, 0.16, 0.45, "4. Newsvendor SS", "Implied σ̂ Derivation\nSS = z_SL × σ̂ × √L\nCapital Optimization", "#c084fc"),
        (0.84, 0.35, 0.14, 0.45, "5. Live Triage UI", "Reliability Score\nRisk Tiering (H/M/L)\nProcurement Escalation", "#f87171"),
    ]

    for x, y, w, h, title, sub, col in boxes:
        # Glow effect
        glow = patches.FancyBboxPatch((x-0.004, y-0.008), w+0.008, h+0.016, boxstyle="round,pad=0.02",
                                      facecolor=col, alpha=0.15, edgecolor="none")
        ax.add_patch(glow)
        
        # Main box
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                      facecolor="#141e30", edgecolor=col, linewidth=2)
        ax.add_patch(rect)

        # Title text
        ax.text(x + w/2, y + h - 0.08, title, ha="center", va="center", color=col,
                fontsize=11, fontweight="bold", fontfamily="sans-serif")
        
        # Divider line
        ax.plot([x + 0.01, x + w - 0.01], [y + h - 0.15, y + h - 0.15], color=col, alpha=0.4, linewidth=1)

        # Subtitle text
        ax.text(x + w/2, y + h/2 - 0.05, sub, ha="center", va="center", color="#cbd5e1",
                fontsize=9.5, linespacing=1.4, fontfamily="sans-serif")

    # Draw connecting arrows
    arrow_props = dict(facecolor="#00e5ff", edgecolor="none", width=0.015, headwidth=0.04, headlength=0.03, alpha=0.8)
    ax.annotate("", xy=(0.215, 0.575), xytext=(0.185, 0.575), arrowprops=arrow_props)
    ax.annotate("", xy=(0.415, 0.575), xytext=(0.385, 0.575), arrowprops=arrow_props)
    ax.annotate("", xy=(0.635, 0.575), xytext=(0.605, 0.575), arrowprops=arrow_props)
    ax.annotate("", xy=(0.835, 0.575), xytext=(0.805, 0.575), arrowprops=arrow_props)

    # Title header at top of diagram
    ax.text(0.5, 0.92, "SUPPLYSHIELD AI — END-TO-END SYSTEM ARCHITECTURE", ha="center", va="center",
            color="#ffffff", fontsize=14, fontweight="bold")
    ax.text(0.5, 0.84, "Domain-Agnostic Decision Support Layer Wrapping Point Forecasts into Calibrated Warehouse Directives",
            ha="center", va="center", color="#94a3b8", fontsize=10.5)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "architecture_diagram.png", dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print("Architecture diagram saved.")

def create_coverage_comparison_chart():
    fig, ax = plt.subplots(figsize=(6.5, 4.2), facecolor="#0b101b")
    ax.set_facecolor("#141e30")

    methods = ["Quantile Reg.\n(Baseline)", "Static Conformal\n(MAPIE)", "SupplyShield ACI\n(Proposed)"]
    overall_cov = [94.4, 91.9, 89.0]
    volatile_cov = [94.0, 94.1, 90.9]

    x = range(len(methods))
    width = 0.32

    bars1 = ax.bar([i - width/2 for i in x], overall_cov, width, label="Overall Coverage", color="#38bdf8", alpha=0.85)
    bars2 = ax.bar([i + width/2 for i in x], volatile_cov, width, label="Volatile Shock Regime", color="#00e5ff", edgecolor="#ffffff", linewidth=1.2)

    # 90% Target Line
    ax.axhline(90.0, color="#ff4b4b", linestyle="--", linewidth=2, label="90% Target Level")

    ax.set_ylabel("Empirical Coverage (%)", color="#cbd5e1", fontsize=10, fontweight="bold")
    ax.set_title("Volatile Shock Coverage: ACI Hits 90% Target vs Baseline Hoarding", color="#ffffff", fontsize=11, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(methods, color="#ffffff", fontsize=9.5, fontweight="bold")
    ax.set_ylim(80, 100)
    ax.tick_params(colors="#94a3b8")
    for spine in ax.spines.values():
        spine.set_color("#283750")

    ax.legend(loc="lower right", facecolor="#0b101b", edgecolor="#283750", labelcolor="#cbd5e1", fontsize=8.5)

    for bar in bars2:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f"{yval:.1f}%", ha="center", va="bottom", color="#00e5ff", fontweight="bold", fontsize=9)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "coverage_comparison_deck.png", dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print("Coverage comparison chart saved.")

if __name__ == "__main__":
    create_architecture_diagram()
    create_coverage_comparison_chart()
