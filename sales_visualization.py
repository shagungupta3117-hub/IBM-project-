"""
Sales Data Visualization
------------------------
Reads sample_sales_data.xlsx and builds a 2x3 dashboard of charts.

Install:  pip install pandas matplotlib openpyxl
Run:      python sales_visualization.py
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# ---------- 1. Load data ----------
FILE = "sample_sales_data.xlsx"
df = pd.read_excel(FILE, sheet_name="Sales Data")

# Drop the "Total" row at the bottom (it has no Order ID date)
df = df.dropna(subset=["Date"])
df["Date"] = pd.to_datetime(df["Date"])
df["Month"] = df["Date"].dt.to_period("M").dt.to_timestamp()

SALES = "Total Sales (INR)"

# Format axis numbers as lakhs, e.g. 12.5L
def lakh(x, _):
    return f"{x / 1e5:.0f}L"

lakh_fmt = FuncFormatter(lakh)

# ---------- 2. Aggregations ----------
by_region = df.groupby("Region")[SALES].sum().sort_values(ascending=False)
by_category = df.groupby("Category")[SALES].sum()
by_month = df.groupby("Month")[SALES].sum()
by_product = df.groupby("Product")[SALES].sum().sort_values()
by_person = df.groupby("Salesperson")[SALES].sum().sort_values()
heat = df.pivot_table(index="Region", columns="Category",
                      values=SALES, aggfunc="sum", fill_value=0)

# ---------- 3. Plot ----------
plt.style.use("seaborn-v0_8-whitegrid")
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Sales Dashboard", fontsize=20, fontweight="bold")

# (a) Sales by region - bar
ax = axes[0, 0]
bars = ax.bar(by_region.index, by_region.values, color="#1F4E78")
ax.set_title("Sales by Region")
ax.yaxis.set_major_formatter(lakh_fmt)
ax.bar_label(bars, labels=[f"{v / 1e5:.1f}L" for v in by_region.values], padding=3)

# (b) Sales share by category - pie
ax = axes[0, 1]
wedges, _ = ax.pie(by_category.values, startangle=90,
                   wedgeprops={"edgecolor": "white"})
pct = by_category / by_category.sum() * 100
ax.legend(wedges, [f"{c}: {p:.1f}%" for c, p in zip(by_category.index, pct)],
          loc="center left", bbox_to_anchor=(1.0, 0.5), frameon=False)
ax.set_title("Sales Share by Category")

# (c) Monthly trend - line
ax = axes[0, 2]
ax.plot(by_month.index, by_month.values, marker="o", color="#C0504D", linewidth=2)
ax.set_title("Monthly Sales Trend")
ax.yaxis.set_major_formatter(lakh_fmt)
ax.tick_params(axis="x", rotation=45)

# (d) Sales by product - horizontal bar
ax = axes[1, 0]
ax.barh(by_product.index, by_product.values, color="#4F81BD")
ax.set_title("Sales by Product")
ax.xaxis.set_major_formatter(lakh_fmt)

# (e) Sales by salesperson - horizontal bar
ax = axes[1, 1]
ax.barh(by_person.index, by_person.values, color="#9BBB59")
ax.set_title("Sales by Salesperson")
ax.xaxis.set_major_formatter(lakh_fmt)

# (f) Region x Category heatmap
ax = axes[1, 2]
im = ax.imshow(heat.values, cmap="Blues", aspect="auto")
ax.set_xticks(range(len(heat.columns)), heat.columns, rotation=30)
ax.set_yticks(range(len(heat.index)), heat.index)
ax.set_title("Region x Category Heatmap")
ax.grid(False)
for i in range(heat.shape[0]):
    for j in range(heat.shape[1]):
        val = heat.values[i, j]
        ax.text(j, i, f"{val / 1e5:.1f}L", ha="center", va="center", fontsize=9,
                color="white" if val > heat.values.max() * 0.5 else "black")
fig.colorbar(im, ax=ax, format=lakh_fmt)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("sales_dashboard.png", dpi=150)
print("Saved: sales_dashboard.png")
plt.show()
