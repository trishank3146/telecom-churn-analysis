"""
Step 4 - Create the charts and a one-page dashboard preview (PNG) from the
SQL results. The interactive version is built in Power BI (see powerbi/).

Usage:  python scripts/make_charts.py
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RESULTS = os.path.join(ROOT, "results")
CHARTS = os.path.join(ROOT, "reports", "charts")

RED, BLUE, GREY = "#d64550", "#2f6eba", "#9aa5b1"
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})


def load(name):
    return pd.read_csv(os.path.join(RESULTS, f"{name}.csv"))


def bar(ax, labels, values, title, color=RED, fmt="{:.1f}%"):
    bars = ax.bar(labels, values, color=color)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_ylim(0, max(values) * 1.2)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height(), fmt.format(v),
                ha="center", va="bottom", fontsize=9)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, name), dpi=150)
    plt.close(fig)


def individual_charts():
    c = load("churn_by_contract")
    fig, ax = plt.subplots(figsize=(6, 4))
    bar(ax, c["Contract"], c["churn_rate_pct"], "Churn rate by contract type")
    save(fig, "churn_by_contract.png")

    t = load("churn_by_tenure_group")
    fig, ax = plt.subplots(figsize=(6, 4))
    bar(ax, t["TenureGroup"], t["churn_rate_pct"], "Churn rate by tenure")
    save(fig, "churn_by_tenure.png")

    i = load("churn_by_internet_service")
    fig, ax = plt.subplots(figsize=(6, 4))
    bar(ax, i["InternetService"], i["churn_rate_pct"], "Churn rate by internet service")
    save(fig, "churn_by_internet_service.png")

    p = load("churn_by_payment_method")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(p["PaymentMethod"][::-1], p["churn_rate_pct"][::-1], color=RED)
    ax.set_title("Churn rate by payment method (%)", loc="left", fontweight="bold")
    save(fig, "churn_by_payment_method.png")

    r = load("revenue_at_risk_by_contract")
    fig, ax = plt.subplots(figsize=(6, 4))
    bar(ax, r["Contract"], r["monthly_revenue_lost"], "Monthly revenue lost by contract ($)",
        color=BLUE, fmt="${:,.0f}")
    save(fig, "revenue_lost_by_contract.png")


def dashboard_preview():
    k = load("overall_kpis").iloc[0]
    contract = load("churn_by_contract")
    tenure = load("churn_by_tenure_group")
    internet = load("churn_by_internet_service")
    segments = load("high_risk_segments").head(6)

    fig = plt.figure(figsize=(14, 8.5), facecolor="white")
    fig.suptitle("Telecom Customer Churn Dashboard", x=0.02, ha="left", fontsize=18, fontweight="bold")
    grid = fig.add_gridspec(3, 4, height_ratios=[0.55, 1.4, 1.4], hspace=0.55, wspace=0.35,
                            left=0.03, right=0.98, top=0.9, bottom=0.05)

    kpis = [("Total customers", f"{int(k.total_customers):,}"),
            ("Churn rate", f"{k.churn_rate_pct:.1f}%"),
            ("Monthly revenue lost", f"${k.monthly_revenue_lost:,.0f}"),
            ("Avg tenure", f"{k.avg_tenure_months:.0f} months")]
    for col, (label, value) in enumerate(kpis):
        ax = fig.add_subplot(grid[0, col])
        ax.axis("off")
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, color="#f0f4f8", transform=ax.transAxes))
        ax.text(0.06, 0.62, value, fontsize=20, fontweight="bold",
                color=RED if "Churn" in label or "lost" in label else "#1f2933", transform=ax.transAxes)
        ax.text(0.06, 0.2, label, fontsize=10, color="#616e7c", transform=ax.transAxes)

    bar(fig.add_subplot(grid[1, 0:2]), contract["Contract"], contract["churn_rate_pct"],
        "Churn rate by contract")
    bar(fig.add_subplot(grid[1, 2:4]), tenure["TenureGroup"], tenure["churn_rate_pct"],
        "Churn rate by tenure")
    bar(fig.add_subplot(grid[2, 0:2]), internet["InternetService"], internet["churn_rate_pct"],
        "Churn rate by internet service", color=BLUE)

    ax = fig.add_subplot(grid[2, 2:4])
    ax.axis("off")
    ax.set_title("Highest-risk segments", loc="left", fontweight="bold")
    rows = [[f"{r.Contract} · {r.InternetService} · {r.TenureGroup}", f"{r.churn_rate_pct:.0f}%",
             f"${r.monthly_revenue_lost:,.0f}"] for r in segments.itertuples()]
    table = ax.table(cellText=rows, colLabels=["Segment", "Churn", "Lost / month"],
                     colWidths=[0.66, 0.14, 0.2], loc="upper left", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.35)
    for (row, _), cell in table.get_celld().items():
        cell.set_edgecolor("#e4e7eb")
        if row == 0:
            cell.set_text_props(fontweight="bold")

    fig.savefig(os.path.join(ROOT, "reports", "dashboard_preview.png"), dpi=130)
    plt.close(fig)


def main():
    os.makedirs(CHARTS, exist_ok=True)
    individual_charts()
    dashboard_preview()
    print("Charts saved to reports/charts/ and reports/dashboard_preview.png")


if __name__ == "__main__":
    main()
