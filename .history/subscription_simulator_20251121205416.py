import sqlite3
import numpy as np
import collections

# Step 1: Define Plans and Constants
PLANS = {
    "Lite": {"price": 20, "included_visits": 2, "extra_visit_price": 15},
    "Standard": {"price": 50, "included_visits": 6, "extra_visit_price": 10},
    "Chronic Care": {"price": 90, "included_visits": 12, "extra_visit_price": 5},
    "Unlimited": {"price": 150, "included_visits": float('inf'), "extra_visit_price": 0}
}
HOSPITAL_COST_PER_VISIT = 30

# Step 2: Set up the database
def setup_database(db_name="healthcare_simulation.db"):
    """Creates and sets up the SQLite database and the results table."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS simulation_results")
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

# Step 3: Simulate user behavior
def simulate_user_visits(user_type):
    """Simulates monthly visits for a user using a Poisson distribution."""
    if user_type == 'low':
        return np.random.poisson(lam=1)
    elif user_type == 'medium':
        return np.random.poisson(lam=4)
    elif user_type == 'high':
        return np.random.poisson(lam=10)
    return 0

# Step 4: Calculate revenue and profit
def calculate_profitability(plan_name, visits):
    """Calculates monthly revenue, cost, and profit for a given plan and visit count."""
    try:
        plan = PLANS[plan_name]
    except KeyError:
        return 0, 0, 0
    
    extra_visits = max(0, visits - plan["included_visits"])
    revenue = plan["price"] + (extra_visits * plan["extra_visit_price"])
    cost = visits * HOSPITAL_COST_PER_VISIT
    profit = revenue - cost
    return revenue, cost, profit

# Step 5: Run the simulation
def run_simulation(db_name="healthcare_simulation.db", num_users=1000):
    """Runs the full simulation and stores results in the database."""
    setup_database(db_name)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    user_types = ['low'] * int(num_users * 0.5) + \
                 ['medium'] * int(num_users * 0.4) + \
                 ['high'] * int(num_users * 0.1)
    np.random.shuffle(user_types)

    results = []
    for user_id in range(num_users):
        user_type = user_types[user_id]
        visits = simulate_user_visits(user_type)
        for plan_name in PLANS.keys():
            revenue, cost, profit = calculate_profitability(plan_name, visits)
            results.append((user_id, user_type, plan_name, visits, revenue, cost, profit))

    cursor.executemany("""
        INSERT INTO simulation_results (user_id, user_type, plan_name, simulated_visits, revenue, cost, profit)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, results)

    conn.commit()
    conn.close()
    print(f"Simulation complete. {len(results)} records inserted.")

# Step 6: Analyze the results (No Pandas)
def analyze_results_native(db_name="healthcare_simulation.db"):
    """Analyzes simulation results using only standard Python and sqlite3."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    print("\n--- Simulation Analysis ---")

    # --- Analysis 1: Average Profit Per Plan (Overall) ---
    print("\nAverage Monthly Profit Per Plan:")
    cursor.execute("""
        SELECT plan_name, AVG(profit) as avg_profit
        FROM simulation_results
        GROUP BY plan_name
        ORDER BY avg_profit DESC
    """)
    for row in cursor.fetchall():
        plan_name, avg_profit = row
        print(f"  {plan_name:<15}: {avg_profit:8.2f}")

    # --- Analysis 2: Average Profit by User Type and Plan ---
    print("\nAverage Monthly Profit by User Type and Plan:")
    cursor.execute("""
        SELECT user_type, plan_name, AVG(profit) as avg_profit
        FROM simulation_results
        GROUP BY user_type, plan_name
        ORDER BY user_type, plan_name
    """)
    
    # Use a dictionary to structure the data for pretty printing
    analysis_data = collections.defaultdict(dict)
    for row in cursor.fetchall():
        user_type, plan_name, avg_profit = row
        analysis_data[user_type][plan_name] = avg_profit

    # Get all plan names for header
    plan_names = sorted(PLANS.keys())
    header = f"{'User Type':<12}" + "".join([f"{p:<15}" for p in plan_names])
    print(header)
    print("-" * len(header))

    # Print rows for each user type
    for user_type in sorted(analysis_data.keys()):
        row_str = f"{user_type:<12}"
        for plan_name in plan_names:
            profit = analysis_data[user_type].get(plan_name, 0.0)
            row_str += f"{profit:<15.2f}"
        print(row_str)

    print("\n--- End of Analysis ---")
    conn.close()

# Main execution block
if __name__ == "__main__":
    run_simulation(num_users=1000)
    analyze_results_native() # Use the new, dependency-free function