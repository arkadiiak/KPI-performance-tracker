"""
Generates a synthetic dataset modelling monthly technician performance
at a multi-location beauty salon chain. All names, locations and figures
are fictional and generated randomly - no real business data is used.
"""
import csv
import random

random.seed(42)

LOCATIONS = ["North Studio", "Riverside", "Market Square", "Garden Court", "Park Lane"]
MONTHS = ["April", "May", "June", "July", "August"]

FIRST_NAMES = ["Olena", "Maria", "Sofia", "Nadia", "Iryna", "Kateryna", "Anna",
               "Vika", "Diana", "Yana", "Alina", "Marta", "Lesia", "Halyna", "Tetiana"]

def make_technicians(n=15):
    techs = []
    for i in range(n):
        techs.append({
            "technician_id": f"T{i+1:03d}",
            "name": f"{FIRST_NAMES[i]} {chr(65+i)}.",
            "location": random.choice(LOCATIONS),
            "base_rate": round(random.uniform(14, 18), 2),
        })
    return techs

def generate_month_record(tech, month):
    hours_worked = round(random.uniform(80, 220), 1)
    efficient_hours = round(hours_worked * random.uniform(0.6, 0.85), 1)
    days_worked = random.randint(10, 26)
    revenue = round(hours_worked * random.uniform(28, 42), 2)
    materials_cost = round(revenue * random.uniform(0.04, 0.06), 2)
    total_clients = random.randint(20, 110)
    old_clients = random.randint(0, min(15, total_clients))

    profitability = round((revenue - materials_cost) / revenue * 100, 2) if revenue else 0
    client_retention = round(old_clients / total_clients * 100, 2) if total_clients else 0
    workload = round(efficient_hours / hours_worked * 100, 2) if hours_worked else 0
    workdays_utilization = round(days_worked / 26 * 100, 2)
    pft_completion = round(random.uniform(75, 105), 2)

    final_score = round(
        profitability * 0.30 +
        client_retention * 0.25 +
        workload * 0.20 +
        workdays_utilization * 0.05 +
        pft_completion * 0.20, 1
    )

    if final_score >= 65:
        tier, bonus = "Top-performer", 200
    elif final_score >= 40:
        tier, bonus = "Reliable", 100
    elif final_score >= 25:
        tier, bonus = "Needs Focus", 0
    else:
        tier, bonus = "At risk", 0

    salary = round(hours_worked * tech["base_rate"], 2)

    return {
        "technician_id": tech["technician_id"],
        "name": tech["name"],
        "location": tech["location"],
        "month": month,
        "hours_worked": hours_worked,
        "efficient_hours": efficient_hours,
        "days_worked": days_worked,
        "revenue": revenue,
        "materials_cost": materials_cost,
        "total_clients": total_clients,
        "old_clients": old_clients,
        "base_rate": tech["base_rate"],
        "salary": salary,
        "profitability_pct": profitability,
        "client_retention_pct": client_retention,
        "workload_pct": workload,
        "workdays_utilization_pct": workdays_utilization,
        "pft_completion_pct": pft_completion,
        "final_score": final_score,
        "tier": tier,
        "bonus_gbp": bonus,
    }

def main():
    technicians = make_technicians()
    rows = []
    for tech in technicians:
        for month in MONTHS:
            rows.append(generate_month_record(tech, month))

    fieldnames = list(rows[0].keys())
    with open("/home/claude/nail-salon-analytics/data/salon_performance.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} rows for {len(technicians)} technicians across {len(MONTHS)} months.")

if __name__ == "__main__":
    main()
