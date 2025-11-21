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
    
    # subscription_simulator.py (continued)
import numpy as np

# Step 3: Simulate user behavior
def simulate_user_visits(user_type):
    """
    Simulates the number of monthly visits for a user based on their type,
    using a Poisson distribution.
    
    Args:
        user_type (str): 'low', 'medium', or 'high'.

    Returns:
        int: The simulated number of visits for a month.
    """
    if user_type == 'low':
        # Low-need users have an average of 1 visit
        return np.random.poisson(lam=1)
    elif user_type == 'medium':
        # Medium-need users have an average of 4 visits
        return np.random.poisson(lam=4)
    elif user_type == 'high':
        # High-need users have an average of 10 visits
        return np.random.poisson(lam=10)
    return 0

# subscription_simulator.py (continued)

# Step 4: Calculate revenue and profit
def calculate_profitability(plan_name, visits):
    """
    Calculates the monthly revenue, cost, and profit for a given plan and visit count.
    """
    try:
        plan = PLANS[plan_name]
    except KeyError:
        print(f"Error: Plan '{plan_name}' not found.")
        return 0, 0, 0

    # Calculate extra visits
    if visits > plan["included_visits"]:
        extra_visits = visits - plan["included_visits"]
    else:
        extra_visits = 0

    # Calculate revenue
    revenue = plan["price"] + (extra_visits * plan["extra_visit_price"])

    # Calculate cost
    cost = visits * HOSPITAL_COST_PER_VISIT

    # Calculate profit
    profit = revenue - cost

    return revenue, cost, profit