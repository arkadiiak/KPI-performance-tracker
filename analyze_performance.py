"""
Salon Performance Analysis
---------------------------
Loads the synthetic technician performance dataset into a local SQLite
database (using the schema.sql file), then uses pandas to analyze
KPI trends, bonus payouts, and location performance.
"""

import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "salon_performance.csv"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"
DB_PATH = BASE_DIR / "python" / "salon_performance.db"


def build_database():
    """Create SQLite db from schema and load CSV data into it."""
    df = pd.read_csv(CSV_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())

    technicians = df[["technician_id", "name", "location", "base_rate"]].drop_duplicates()
    technicians.to_sql("technicians", conn, if_exists="replace", index=False)

    performance_cols = [c for c in df.columns if c not in ("name", "location", "base_rate")]
    df[performance_cols].to_sql("monthly_performance", conn, if_exists="append", index=False)

    conn.commit()
    return conn


def top_performers_by_month(conn, top_n=3):
    query = """
        SELECT m.month, t.name, t.location, m.final_score, m.tier
        FROM monthly_performance m
        JOIN technicians t ON t.technician_id = m.technician_id
        ORDER BY m.month, m.final_score DESC
    """
    df = pd.read_sql(query, conn)
    return df.groupby("month").head(top_n)


def location_summary(conn):
    query = """
        SELECT t.location, m.month, SUM(m.revenue) AS revenue,
               AVG(m.final_score) AS avg_score
        FROM monthly_performance m
        JOIN technicians t ON t.technician_id = m.technician_id
        GROUP BY t.location, m.month
    """
    return pd.read_sql(query, conn)


def bonus_payout_summary(conn):
    query = """
        SELECT month, tier, COUNT(*) AS headcount, SUM(bonus_gbp) AS total_bonus
        FROM monthly_performance
        GROUP BY month, tier
    """
    return pd.read_sql(query, conn)


def plot_location_revenue(location_df):
    import matplotlib.pyplot as plt

    pivot = location_df.pivot(index="month", columns="location", values="revenue")
    month_order = ["April", "May", "June", "July", "August"]
    pivot = pivot.reindex(month_order)

    ax = pivot.plot(kind="line", marker="o", figsize=(9, 5))
    ax.set_title("Monthly Revenue by Location")
    ax.set_ylabel("Revenue (£)")
    ax.set_xlabel("Month")
    plt.tight_layout()
    plt.savefig(BASE_DIR / "python" / "revenue_by_location.png")
    print("Chart saved to python/revenue_by_location.png")


def main():
    conn = build_database()

    print("\n=== Top performers by month ===")
    print(top_performers_by_month(conn).to_string(index=False))

    loc_df = location_summary(conn)
    print("\n=== Location summary ===")
    print(loc_df.to_string(index=False))

    print("\n=== Bonus payout summary ===")
    print(bonus_payout_summary(conn).to_string(index=False))

    plot_location_revenue(loc_df)

    conn.close()


if __name__ == "__main__":
    main()
