# synthetic_data_generator.py
"""Generate synthetic running data for DynamoDB tables"""

import csv
import random
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal

# Configuration
USER_ID = "540894c8-b0f1-7079-e1b3-4c93e1f7ed5e"
START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 6, 14)
YEARLY_TARGET = 1000  # km
NOTES_OPTIONS = ["Recovery", "Tempo", "Interval", "Long"]


def generate_run_id():
    """Generate a unique run ID"""
    return str(uuid.uuid4())


def generate_target_id():
    """Generate a unique target ID"""
    return str(uuid.uuid4())


def calculate_duration_from_pace(distance_km, pace_min_per_km):
    """Calculate duration in HH:MM:SS format from distance and pace"""
    total_minutes = distance_km * pace_min_per_km
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    seconds = int((total_minutes % 1) * 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def calculate_duration_seconds(distance_km, pace_min_per_km):
    """Calculate duration in seconds"""
    total_minutes = distance_km * pace_min_per_km
    return int(total_minutes * 60)


def generate_realistic_runs():
    """Generate realistic running pattern with progressive training"""
    runs = []
    current_date = START_DATE

    # Track running pattern
    runs_this_week = 0
    days_since_last_run = 0
    weekly_distance = 0.0

    # Progressive monthly targets (building up to ~100km/month)
    monthly_distance_targets = {
        1: 60,  # January - building up
        2: 70,  # February
        3: 80,  # March
        4: 90,  # April
        5: 100,  # May - target pace
        6: 50,  # June (partial month through 14th)
    }

    while current_date <= END_DATE:
        # Determine if we should run today
        is_weekend = current_date.weekday() >= 5  # Saturday=5, Sunday=6
        is_saturday = current_date.weekday() == 5

        # Rest period logic (random breaks)
        if random.random() < 0.02:  # 2% chance of starting a short break
            days_since_last_run = random.randint(3, 5)
        elif random.random() < 0.005:  # 0.5% chance of longer break
            days_since_last_run = random.randint(7, 14)

        # Should we run today?
        should_run = (
            days_since_last_run == 0
            and runs_this_week < 6  # Max 6 runs per week
            and (
                (not is_weekend and random.random() < 0.7)  # 70% chance weekday
                or (
                    is_saturday and random.random() < 0.9
                )  # 90% chance Saturday (long run day)
                or (is_weekend and random.random() < 0.4)  # 40% chance Sunday
            )
        )

        if should_run:
            # Generate run details
            if is_saturday and runs_this_week >= 2:
                # Saturday long run
                distance = random.uniform(8, 15)
                notes = "Long"
                pace = random.uniform(7.0, 8.0)  # Slower for long runs
            else:
                # Regular run
                distance = random.uniform(3, 8)
                notes = random.choice(["Recovery", "Tempo", "Interval"])
                if notes == "Recovery":
                    pace = random.uniform(7.5, 8.0)
                elif notes == "Tempo":
                    pace = random.uniform(6.5, 7.0)
                else:  # Interval
                    pace = random.uniform(6.3, 6.8)

            # Create run record
            run = {
                "user_id": USER_ID,
                "run_id": generate_run_id(),
                "date": current_date.isoformat(),
                "distance_km": round(distance, 2),
                "duration_seconds": calculate_duration_seconds(distance, pace),
                "notes": notes,
                "created_at": datetime.utcnow().isoformat(),
            }

            runs.append(run)
            runs_this_week += 1
            weekly_distance += distance
            days_since_last_run = 0
        else:
            days_since_last_run = max(0, days_since_last_run - 1)

        # Reset weekly counters on Monday
        if current_date.weekday() == 0:  # Monday
            runs_this_week = 0
            weekly_distance = 0.0

        current_date += timedelta(days=1)

    return runs


def generate_targets():
    """Generate yearly and monthly targets"""
    targets = []

    # Yearly target for 2025
    yearly_target = {
        "user_id": USER_ID,
        "target_id": generate_target_id(),
        "target_type": "yearly",
        "period": "2025",
        "distance_km": YEARLY_TARGET,
        "created_at": datetime(2024, 12, 31).isoformat(),  # Set at end of previous year
    }
    targets.append(yearly_target)

    # Monthly targets (progressive plan)
    monthly_targets = {
        "2025-01": 80,  # January - ambitious start
        "2025-02": 75,  # February - slightly less (shorter month)
        "2025-03": 85,  # March - building up
        "2025-04": 90,  # April
        "2025-05": 100,  # May - peak
        "2025-06": 95,  # June - maintaining
    }

    for period, distance in monthly_targets.items():
        monthly_target = {
            "user_id": USER_ID,
            "target_id": generate_target_id(),
            "target_type": "monthly",
            "period": period,
            "distance_km": distance,
            "created_at": datetime(2024, 12, 31).isoformat(),
        }
        targets.append(monthly_target)

    return targets


def write_csv_files(runs, targets):
    """Write runs and targets to CSV files"""

    # Write runs CSV
    runs_filename = "synthetic_runs_data.csv"
    with open(runs_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "user_id",
                "run_id",
                "date",
                "distance_km",
                "duration_seconds",
                "notes",
                "created_at",
            ],
        )
        writer.writeheader()
        writer.writerows(runs)

    # Write targets CSV
    targets_filename = "synthetic_targets_data.csv"
    with open(targets_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "user_id",
                "target_id",
                "target_type",
                "period",
                "distance_km",
                "created_at",
            ],
        )
        writer.writeheader()
        writer.writerows(targets)

    return runs_filename, targets_filename


def main():
    """Generate complete synthetic dataset"""
    print("Generating synthetic running data...")
    print(f"Date range: {START_DATE} to {END_DATE}")
    print(f"User ID: {USER_ID}")
    print(f"Yearly target: {YEARLY_TARGET}km")
    print()

    # Generate runs
    print("Generating runs...")
    runs = generate_realistic_runs()

    # Generate targets
    print("Generating targets...")
    targets = generate_targets()

    # Write CSV files
    print("Writing CSV files...")
    runs_file, targets_file = write_csv_files(runs, targets)

    # Summary
    total_distance = sum(run["distance_km"] for run in runs)
    print(f"\n=== SUMMARY ===")
    print(f"Generated {len(runs)} runs")
    print(f"Generated {len(targets)} targets ({len(targets)-1} monthly + 1 yearly)")
    print(f"Total distance: {total_distance:.1f}km")
    print(f"Average per run: {total_distance/len(runs):.1f}km")

    # Monthly breakdown
    monthly_totals = {}
    for run in runs:
        month = int(run["date"].split("-")[1])
        monthly_totals[month] = monthly_totals.get(month, 0) + run["distance_km"]

    print(f"\nMonthly totals:")
    for month in sorted(monthly_totals.keys()):
        print(f"  Month {month:2d}: {monthly_totals[month]:6.1f}km")

    print(f"\nFiles created:")
    print(f"  - {runs_file}")
    print(f"  - {targets_file}")
    print(f"\nReady for S3 upload and DynamoDB import!")


if __name__ == "__main__":
    main()
