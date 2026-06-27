"""
SupplyShield AI — Professional System Architecture Diagram Generator
Outputs a high-resolution, layered software architecture diagram matching app.py & main.py.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Setup Figure
fig, ax = plt.subplots(figsize=(14, 10), dpi=300)
BG = "#080c16"
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis("off")

# Colors
WHITE = "#ffffff"
SLATE = "#cbd5e1"
MUTED = "#64748b"
CYAN  = "#00e5ff"
GOLD  = "#fbbf24"
PURP  = "#a78bfa"
BLUE  = "#38bdf8"
CARD_BG = "#0d1424"

# Title Header
ax.text(7.0, 9.4, "SUPPLYSHIELD AI — SYSTEM ARCHITECTURE & DATA FLOW",
        color=WHITE, fontsize=18, fontweight="bold", ha="center", va="center", fontfamily="sans-serif")
ax.text(7.0, 9.0, "Probabilistic Supply Chain Risk Triage & Adaptive Conformal Inference Platform",
        color=CYAN, fontsize=12, fontweight="bold", ha="center", va="center", fontfamily="sans-serif")
ax.plot([1.0, 13.0], [8.65, 8.65], color=MUTED, lw=1.0, alpha=0.5)

# Helper function to draw layer frames
def draw_layer(y, height, border_col, title, subtitle):
    # Layer Background Frame
    frame = FancyBboxPatch((0.6, y), 12.8, height, boxstyle="round,pad=0.15",
                           facecolor=CARD_BG, edgecolor=border_col, linewidth=2.0, zorder=2, alpha=0.9)
    ax.add_patch(frame)
    # Layer Title
    ax.text(1.0, y + height - 0.35, title, color=border_col, fontsize=12, fontweight="bold", ha="left", va="center", zorder=4)
    ax.text(1.0, y + height - 0.65, subtitle, color=MUTED, fontsize=9.5, ha="left", va="center", zorder=4)
    ax.plot([1.0, 13.0], [y + height - 0.85, y + height - 0.85], color=border_col, lw=0.8, alpha=0.3, zorder=3)

# Helper function to draw component boxes inside layers
def draw_component(x, y, w, h, col, title, bullets):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                         facecolor="#121b30", edgecolor=col, linewidth=1.5, zorder=4)
    ax.add_patch(box)
    ax.text(x + w/2, y + h - 0.3, title, color=WHITE, fontsize=10.5, fontweight="bold", ha="center", va="center", zorder=5)
    ax.plot([x + 0.15, x + w - 0.15], [y + h - 0.5, y + h - 0.5], color=col, lw=0.8, alpha=0.5, zorder=5)
    for i, bullet in enumerate(bullets):
        ax.text(x + 0.2, y + h - 0.85 - (i * 0.35), bullet, color=SLATE, fontsize=9, ha="left", va="center", zorder=5)

# Helper function for vertical arrows between layers
def draw_arrow(x, y1, y2, label):
    ax.annotate("", xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.3", color=WHITE, lw=2.0), zorder=6)
    ax.text(x + 0.15, (y1 + y2)/2, label, color=CYAN, fontsize=8.5, fontweight="bold", ha="left", va="center", zorder=6,
            bbox=dict(facecolor=BG, edgecolor="none", pad=1.0))

# ── TIER 4: PRESENTATION & UI LAYER (Top) ──
draw_layer(6.6, 1.8, CYAN, "1. PRESENTATION & EXECUTIVE UI LAYER (Streamlit Web Application)", "Interactive Risk Command Center & Dynamic Decision Triage")
draw_component(1.0, 6.8, 3.6, 1.0, CYAN, "Executive Landing Page", ["• Cyber-Obsidian Design System", "• Live System Calibration Status"])
draw_component(5.1, 6.8, 3.8, 1.0, CYAN, "Interactive Triage Table", ["• Dynamic Multi-Select Filters", "• Instant High/Med/Low Sorting"])
draw_component(9.3, 6.8, 3.7, 1.0, CYAN, "Visual Evidence Explorer", ["• Empirical Coverage Graphs", "• Adaptive Alpha Trajectory"])

# Arrow UI <-> Decision
draw_arrow(7.0, 6.6, 6.1, "Filtered SKU Directives & Escalation Alerts")

# ── TIER 3: DECISION & INVENTORY LAYER ──
draw_layer(4.3, 1.8, GOLD, "2. DECISION & INVENTORY OPTIMIZATION LAYER (Newsvendor Theory)", "Translating Uncertainty Bounds into Floor-Ready Warehouse Directives")
draw_component(1.0, 4.5, 3.6, 1.0, GOLD, "Empirical Volatility (σ̂)", ["• Extracted from ACI Interval", "• σ̂ = (U_t - L_t) / (2 × 1.645)"])
draw_component(5.1, 4.5, 3.8, 1.0, GOLD, "Safety Stock Formulation", ["• Newsvendor Buffer Calculation", "• SS = z_SL × σ̂ × √(Lead Time)"])
draw_component(9.3, 4.5, 3.7, 1.0, GOLD, "Automated Escalation Protocol", ["• 0-100 Reliability Trust Index", "• 'Escalate to Procurement' Flag"])

# Arrow Decision <-> AI
draw_arrow(7.0, 4.3, 3.8, "Calibrated 90% Prediction Intervals [L_t, U_t]")

# ── TIER 2: AI & CALIBRATION ENGINE LAYER ──
draw_layer(2.0, 1.8, PURP, "3. AI FORECASTING & UNCERTAINTY CALIBRATION LAYER", "Rigorous Statistical Engine with Dynamic Shocks Adaptation")
draw_component(1.0, 2.2, 3.6, 1.0, PURP, "Base LightGBM Forecaster", ["• Quantile Regression Engine", "• Rolling-Origin Cross Validation"])
draw_component(5.1, 2.2, 3.8, 1.0, PURP, "Static Conformal Baseline", ["• MAPIE Split Conformal Regressor", "• Fails during Demand Shocks"])
draw_component(9.3, 2.2, 3.7, 1.0, PURP, "Adaptive Conformal (ACI)", ["• Gibbs & Candès (2022) Physics", "• α_{t+1} = α_t + γ(α - err_t)"])

# Arrow AI <-> Data
draw_arrow(7.0, 2.0, 1.5, "Engineered Features, Lags & Rolling Volatility")

# ── TIER 1: DATA PIPELINE LAYER (Bottom) ──
draw_layer(0.3, 1.2, BLUE, "4. DATA INGESTION & FEATURE ENGINEERING LAYER", "Real-World Enterprise Retail Supply Chain Data")
draw_component(1.0, 0.45, 5.8, 0.7, BLUE, "Walmart M5 Competition Dataset", ["• 66,950 Train Rows | 14,350 Test Evaluation Rows"])
draw_component(7.2, 0.45, 5.8, 0.7, BLUE, "Volatility Regime Splitter", ["• 83.4% Volatile Demand Periods Identified & Separated"])

plt.tight_layout(pad=0.5)
out_path = r"C:\Users\Asus\OneDrive\Desktop\SupplyChain AI\SupplyShield_System_Architecture.png"
plt.savefig(out_path, dpi=300, facecolor=BG, edgecolor="none")
plt.close()
print(f"[OK] System architecture diagram successfully generated at:\n{out_path}")
