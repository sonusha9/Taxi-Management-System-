from collections import defaultdict
from datetime import datetime, timedelta


def _parse_ride_date(ride):
    if isinstance(ride.completed_at, datetime):
        return ride.completed_at
    return datetime.fromisoformat(str(ride.completed_at))


def generate_management_report(drivers, customers, rides, completed_customers):
    """Build a text management report with key statistics."""
    now = datetime.now()
    today = now.date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    daily = weekly = monthly = 0
    revenue_daily = revenue_weekly = revenue_monthly = 0.0
    rides_per_driver = defaultdict(int)
    revenue_per_driver = defaultdict(float)

    for ride in rides:
        ride_date = _parse_ride_date(ride).date()
        rides_per_driver[ride.driver_name] += 1
        revenue_per_driver[ride.driver_name] += ride.fare

        if ride_date == today:
            daily += 1
            revenue_daily += ride.fare
        if ride_date >= week_start:
            weekly += 1
            revenue_weekly += ride.fare
        if ride_date >= month_start:
            monthly += 1
            revenue_monthly += ride.fare

    status_counts = defaultdict(int)
    for d in drivers:
        status_counts[d.get_status()] += 1

    lines = [
        "=" * 55,
        "         TAXI MANAGEMENT REPORT",
        "=" * 55,
        "",
        "OVERVIEW",
        f"  Total Drivers:            {len(drivers)}",
        f"  Total Active Customers:   {len(customers)}",
        f"  Total Completed Rides:    {len(rides)}",
        f"  Completed Customers:      {len(completed_customers)}",
        "",
        "DRIVER STATUS",
        f"  Available:                {status_counts.get('Available', 0)}",
        f"  On Ride:                  {status_counts.get('On Ride', 0)}",
        f"  Offline:                  {status_counts.get('Offline', 0)}",
        "",
        "RIDE VOLUME",
        f"  Rides Today:              {daily}",
        f"  Rides This Week:          {weekly}",
        f"  Rides This Month:         {monthly}",
        "",
        "REVENUE",
        f"  Revenue Today:            £{revenue_daily:,.2f}",
        f"  Revenue This Week:        £{revenue_weekly:,.2f}",
        f"  Revenue This Month:       £{revenue_monthly:,.2f}",
        f"  Total Revenue (All Time): £{sum(r.fare for r in rides):,.2f}",
        "",
        "RIDES PER DRIVER",
    ]

    if rides_per_driver:
        for name, count in sorted(rides_per_driver.items(), key=lambda x: -x[1]):
            rev = revenue_per_driver[name]
            lines.append(f"  {name:<25} {count:>4} rides   £{rev:>8,.2f}")
    else:
        lines.append("  No completed rides yet.")

    lines.extend(["", "=" * 55])
    return "\n".join(lines)


def rides_by_period(rides):
    """Return daily counts for the last 7 days and monthly for last 6 months."""
    now = datetime.now()
    daily_labels = []
    daily_counts = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).date()
        daily_labels.append(day.strftime("%a %d"))
        daily_counts.append(
            sum(1 for r in rides if _parse_ride_date(r).date() == day)
        )

    monthly_labels = []
    monthly_counts = []
    year, month = now.year, now.month
    for _ in range(6):
        label = datetime(year, month, 1).strftime("%b %Y")
        monthly_labels.insert(0, label)
        count = sum(
            1
            for r in rides
            if _parse_ride_date(r).year == year and _parse_ride_date(r).month == month
        )
        monthly_counts.insert(0, count)
        month -= 1
        if month == 0:
            month = 12
            year -= 1

    return {
        "daily_labels": daily_labels,
        "daily_counts": daily_counts,
        "monthly_labels": monthly_labels,
        "monthly_counts": monthly_counts,
    }
