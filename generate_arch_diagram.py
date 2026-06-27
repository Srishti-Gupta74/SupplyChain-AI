"""
SupplyShield AI — Ultra-Clear, High-Contrast Architecture Diagram
Designed specifically for 1080p/4K presentation screens with huge, legible fonts.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# Match slide dimensions exactly so font sizes render 1:1 true to size
fig, ax = plt.subplots(figsize=(12, 5.5), dpi=300)

BG    = "#060a14"
CARD  = "#0e1526"
CYAN  = "#00dcff"
BLUE  = "#38bdf8"
PURP  = "#a78bfa"
GOLD  = "#fbbf24"
WHITE = "#ffffff"
SLATE = "#dce6f5"
MUTED = "#64748b"

fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 12)
ax.set_ylim(0, 5.5)
ax.axis("off")

# Title
ax.text(6.0, 5.15, "SUPPLYSHIELD AI — END-TO-END SYSTEM ARCHITECTURE",
        color=WHITE, fontsize=16, fontweight="bold", ha="center", va="center")
ax.plot([0.5, 11.5], [4.85, 4.85], color=CYAN, lw=2.0)

# 4 Core Architectural Pillars
nodes = [
    # (x, color, step_num, title, lines)
    (0.5, BLUE, "STEP 1", "DATA PIPELINE", [
        "• Walmart M5 Competition",
        "• 83.4% Volatile SKUs",
        "• Rolling Time-Series Split",
        "• Lags & Demand CV > 0.3"
    ]),
    (3.35, PURP, "STEP 2", "AI FORECASTER", [
        "• LightGBM Model",
        "• Quantile Regression",
        "• MAE Optimized Engine",
        "• Raw Uncertainty Bounds"
    ]),
    (6.2, CYAN, "STEP 3", "ACI CALIBRATION", [
        "• Gibbs & Candès (2022)",
        "• Adaptive Conformal Inf.",
        "• Auto-Widens on Shock",
        "• 90.9% SLA Guarantee"
    ]),
    (9.05, GOLD, "STEP 4", "DECISION ENGINE", [
        "• Newsvendor Safety Stock",
        "• Dynamic Buffer Sizing",
        "• +66.7% Stockouts Saved",
        "• Automated Escalations"
    ])
]

box_w = 2.45
box_h = 3.8
box_y = 0.6

for x, col, step, title, lines in nodes:
    # Outer Card
    card = FancyBboxPatch((x, box_y), box_w, box_h,
                          boxstyle="round,pad=0.1",
                          facecolor=CARD, edgecolor=col, linewidth=2.5, zorder=3)
    ax.add_patch(card)
    
    # Top Accent Header
    header = FancyBboxPatch((x, box_y + box_h - 0.65), box_w, 0.65,
                            boxstyle="round,pad=0.1",
                            facecolor=col, edgecolor="none", zorder=4)
    ax.add_patch(header)
    
    # Square off bottom of header
    ax.fill_between([x, x + box_w], [box_y + box_h - 0.65]*2, [box_y + box_h - 0.3]*2, color=col, zorder=4)
    
    # Header Text (Step + Title)
    ax.text(x + box_w/2, box_y + box_h - 0.22, step,
            color="#000000", fontsize=10, fontweight="bold", ha="center", va="center", zorder=5)
    ax.text(x + box_w/2, box_y + box_h - 0.48, title,
            color="#000000", fontsize=13, fontweight="bold", ha="center", va="center", zorder=5)
    
    # Bullet Points
    start_y = box_y + box_h - 1.1
    spacing = 0.62
    for i, line in enumerate(lines):
        # Highlight key statistical results
        text_col = WHITE if ("%" in line or "Guarantee" in line or "Saved" in line) else SLATE
        weight = "bold" if ("%" in line or "Guarantee" in line or "Saved" in line) else "normal"
        
        ax.text(x + 0.18, start_y - (i * spacing), line,
                color=text_col, fontsize=11.5, fontweight=weight, ha="left", va="center", zorder=5)

# Connecting Arrows
arrow_y = box_y + (box_h / 2) - 0.3
for i in range(3):
    x_start = nodes[i][0] + box_w + 0.05
    x_end = nodes[i+1][0] - 0.05
    ax.annotate("", xy=(x_end, arrow_y), xytext=(x_start, arrow_y),
                arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.4", 
                                color=CYAN, lw=3.5), zorder=6)

# Footer
ax.text(6.0, 0.2, "Mathematical Rigor Translated into Floor-Ready Supply Chain Resilience",
        color=MUTED, fontsize=11, fontweight="bold", ha="center", va="center", style="italic")

plt.tight_layout(pad=0.2)
plt.savefig("outputs/architecture_diagram_pro.png", dpi=300, facecolor=BG, edgecolor="none")
plt.close()
print("[OK] Ultra-clear architecture diagram generated successfully.")
