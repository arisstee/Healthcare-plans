import sqlite3
import random
import numpy as np # Optional, but standard random is fine too
import pandas as pd # Used for nice display, can be done with standard CSV logic
import matplotlib.pyplot as plt

# --- 1. CONFIGURATION & PLANS (Based on Page 1) ---
COST_PER_VISIT = 10  # Cost to the hospital per visit

class Plan:
    def __init__(self, name, monthly_price, included_visits, extra_visit_price):
        self.name = name
        self.monthly_price = monthly_price
        self.included_visits = included_visits
        self.extra_visit_price = extra_visit_price

    def calculate_annual_economics(self, annual_visits):
        """Calculates Revenue, Cost, and Profit for one user over 12 months."""
        # Revenue = (Monthly Fee * 12) + (Extra Visits * Extra Price)
        # Note: In reality, 'included' is usually per month. 
        # We will simulate month-by-month for accuracy.
        
        # We assume annual_visits are distributed roughly evenly, 
        # but to be precise, we should calculate overage monthly.
        # For simplicity in this aggregation:
        monthly_avg_visits = annual_visits / 12
        
        # Calculate monthly overage
        if self.included_visits == float('inf'):
            monthly_overage = 0
        else:
            monthly_overage = max(0, monthly_avg_visits - self.included_visits)
            
        annual_revenue = (self.monthly_price * 12) + (monthly_overage * 12 * self.extra_visit_price)
        annual_cost = annual_visits * COST_PER_VISIT
        annual_profit = annual_revenue - annual_cost
        
        return annual_revenue, annual_cost, annual_profit

# Define Plans from Page 1
plans = [
    Plan("Lite", 20, 2, 15),
    Plan("Standard", 50, 6, 10),
    Plan("Chronic", 90, 12, 5),
    Plan("Unlimited", 150, float('inf'), 0)
]

# --- 2. DATABASE SETUP (SQLite) ---
def init_db():
    conn = sqlite3.connect('healthcare_simulation.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS simulation_results')
    c.execute('''
        CREATE TABLE simulation_results (
            user_id INTEGER PRIMARY KEY,
            user_type TEXT,
            annual_visits INTEGER,
            best_plan TEXT,
            plan_revenue REAL,
            plan_cost REAL,
            plan_profit REAL
        )
    ''')
    conn.commit()
    return conn

# --- 3. SIMULATION ENGINE ---
def run_simulation(num_users=1000):
    conn = init_db()
    c = conn.cursor()
    
    results = []
    
    for user_id in range(1, num_users + 1):
        # assign user type and Poisson Lambda (avg visits per month)
        rand_val = random.random()
        if rand_val < 0.50:
            u_type, lam = "Healthy", 0.2
        elif rand_val < 0.80:
            u_type, lam = "Average", 0.6
        else:
            u_type, lam = "Chronic", 2.5
            
        # Simulate 12 months of visits
        total_visits = sum([np.random.poisson(lam) for _ in range(12)])
        
        # Determine which plan is best for the COMPANY (Max Profit) 
        # OR best for the USER (Lowest Cost). 
        # Let's simulate that users pick the plan that minimizes THEIR cost.
        
        best_plan_name = ""
        lowest_user_cost = float('inf')
        company_metrics = (0,0,0) # Rev, Cost, Profit
        
        for plan in plans:
            # Rev to company is Cost to user
            rev, cost, profit = plan.calculate_annual_economics(total_visits)
            
            # User chooses plan with lowest annual expense (Revenue)
            if rev < lowest_user_cost:
                lowest_user_cost = rev
                best_plan_name = plan.name
                company_metrics = (rev, cost, profit)
        
        # Store Data
        c.execute('''
            INSERT INTO simulation_results VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, u_type, total_visits, best_plan_name, 
              company_metrics[0], company_metrics[1], company_metrics[2]))
        
    conn.commit()
    return conn

# --- 4. ANALYSIS & PRESENTATION ---
def analyze_results(conn):
    # Load into DataFrame for easy analysis
    df = pd.read_sql_query("SELECT * FROM simulation_results", conn)
    
    print("--- SIMULATION REPORT ---")
    print(f"Total Users: {len(df)}")
    print(f"Total Company Profit: €{df['plan_profit'].sum():,.2f}")
    print(f"Avg Profit per User: €{df['plan_profit'].mean():,.2f}")
    print("\nPlan Distribution (What users chose):")
    print(df['best_plan'].value_counts())
    
    print("\nFinancials by User Type:")
    print(df.groupby('user_type')[['annual_visits', 'plan_revenue', 'plan_profit']].mean())

    # Optional: Visualization
    plt.figure(figsize=(10, 6))
    for u_type in df['user_type'].unique():
        subset = df[df['user_type'] == u_type]
        plt.hist(subset['annual_visits'], alpha=0.5, label=u_type, bins=range(0, 50))
    
    plt.title('Distribution of Annual Visits by User Type')
    plt.xlabel('Visits per Year')
    plt.ylabel('Number of Users')
    plt.legend()
    plt.show()

# Run it
if __name__ == "__main__":
    connection = run_simulation(1000)
    analyze_results(connection)
    connection.close()