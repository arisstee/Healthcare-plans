# subscription_simulator.py

# Step 1: Define Plans and Constants

# Dictionary to hold the details of each subscription plan
PLANS = {
    "Lite": {
        "price": 20,
        "included_visits": 2,
        "extra_visit_price": 15
    },
    "Standard": {
        "price": 50,
        "included_visits": 6,
        "extra_visit_price": 10
    },
    "Chronic Care": {
        "price": 90,
        "included_visits": 12,
        "extra_visit_price": 5
    },
    "Unlimited": {
        # Using float('inf') for unlimited visits is a good way to handle this case in code
        "price": 150,
        "included_visits": float('inf'),
        "extra_visit_price": 0
    }
}

# The hospital's internal cost for a single patient visit
HOSPITAL_COST_PER_VISIT = 30 # This is a more realistic cost assumption

# subscription_simulator.py (continued)
import sqlite3

# Step 2: Set up the database
def setup_database(db_name="healthcare_simulation.db"):
    """
    Creates and sets up the SQLite database and the results table.
    Deletes existing table to ensure a fresh simulation run every time.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Drop the table if it already exists to avoid duplicate data from previous runs
    cursor.execute("DROP TABLE IF EXISTS simulation_results")

    # Create the table to store results
    cursor.execute("""
        CREATE TABLE simulation_results (
            user_id INTEGER,
            user_type TEXT,
            plan_name TEXT,
            simulated_visits INTEGER,
            revenue REAL,
            cost REAL,
            profit REAL
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database '{db_name}' set up successfully.")