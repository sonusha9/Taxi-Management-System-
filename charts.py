import os
import tempfile

import matplotlib.pyplot as plt
from collections import defaultdict

from reports import rides_by_period


STATUS_COLORS = {
    "Available": "#2ecc71",
    "On Ride": "#f39c12",
    "Offline": "#95a5a6",
}


def _save_fig(fig, prefix="chart"):
    path = os.path.join(tempfile.gettempdir(), f"taxi_{prefix}.png")
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return path


def chart_daily_rides(rides):
    data = rides_by_period(rides)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(data["daily_labels"], data["daily_counts"], color="#3498db")
    ax.set_title("Daily Rides (Last 7 Days)")
    ax.set_ylabel("Number of Rides")
    ax.set_xlabel("Day")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    return _save_fig(fig, "daily_rides")


def chart_monthly_rides(rides):
    data = rides_by_period(rides)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(data["monthly_labels"], data["monthly_counts"], color="#9b59b6")
    ax.set_title("Monthly Rides (Last 6 Months)")
    ax.set_ylabel("Number of Rides")
    ax.set_xlabel("Month")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    return _save_fig(fig, "monthly_rides")


def chart_driver_status(drivers):
    counts = defaultdict(int)
    for d in drivers:
        counts[d.get_status()] += 1

    labels = list(counts.keys()) or ["No Drivers"]
    values = list(counts.values()) or [1]
    colors = [STATUS_COLORS.get(l, "#bdc3c7") for l in labels]

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(values, labels=labels, autopct="%1.0f%%", colors=colors, startangle=90)
    ax.set_title("Driver Status Distribution")
    fig.tight_layout()
    return _save_fig(fig, "driver_status")


def chart_rides_per_driver(rides):
    counts = defaultdict(int)
    for r in rides:
        counts[r.driver_name] += 1

    if not counts:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, "No ride data yet", ha="center", va="center", fontsize=14)
        ax.axis("off")
        return _save_fig(fig, "rides_per_driver")

    names = list(counts.keys())
    values = list(counts.values())
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(names, values, color="#e74c3c")
    ax.set_title("Rides per Driver")
    ax.set_xlabel("Number of Rides")
    fig.tight_layout()
    return _save_fig(fig, "rides_per_driver")


def chart_revenue_by_driver(rides):
    revenue = defaultdict(float)
    for r in rides:
        revenue[r.driver_name] += r.fare

    if not revenue:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, "No revenue data yet", ha="center", va="center", fontsize=14)
        ax.axis("off")
        return _save_fig(fig, "revenue_driver")

    names = list(revenue.keys())
    values = list(revenue.values())
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(names, values, color="#1abc9c")
    ax.set_title("Revenue by Driver (£)")
    ax.set_ylabel("Revenue (£)")
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    return _save_fig(fig, "revenue_driver")
