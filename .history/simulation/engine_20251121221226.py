import sqlite3
import random
import math

# Attempt to import numpy for efficient Poisson distribution generation.
# If not available, we fall back to a standard Python implementation.
try:
    import numpy as np
    USE_NUMPY = True
except ImportError:
    USE_NUMPY = False

class SimulationEngine:
    """
    A standalone engine to simulate user behavior and financial outcomes 
    for healthcare subscription plans.
    
    This engine:
    1. Simulates user segments (Healthy, Average, Chronic).
    2. Generates random monthly doctor visits using a Poisson distribution.
    3. Calculates the most cost-effective plan for each user.
    4. Computes the Company's Revenue, Cost, and Profit.
    """

    def __init__(self, db_path='healthcare_simulation.db'):
        self.db_path = db_path
        self.cost_per_visit = 10  # The hospital's internal cost to provide one visit
        
        # Define Subscription Plans (Based on requirements)
        self.plans = [
            {"name": "Lite", "price": 20, "included": 2, "extra": 15},
            {"name": "Standard", "price": 50, "included": 6, "extra": 10},
            {"name": "Chronic", "price": 90, "included": 12, "extra": 5},
            {"name": "Unlimited", "price": 150, "included": float('inf'), "extra": 0}
        ]

    def _generate_poisson_visit(self, lam):
        """Generate a single month's visit count based on Lambda (avg visits)."""
        if USE_NUMPY:
            return np.random.poisson(lam)
        else:
            # Knuth's algorithm for Poisson distribution (fallback)
            L = math.exp(-lam)
            k = 0
            p = 1.0
            while p > L:
                k += 1
                p *= random.random()
            return k - 1

    def setup_db(self):
        """Initialize the SQLite database for simulation results."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('DROP TABLE IF EXISTS simulation_results')
        c.execute('''
            CREATE TABLE simulation_results (
                user_id INTEGER PRIMARY KEY,
                user_type TEXT,
                annual_visits INTEGER,
                chosen_plan TEXT,
                user_annual_cost REAL,
                company_revenue REAL,
                company_cost REAL,
                company_profit REAL
            )
        ''')
        conn.commit()
        conn.close()

    def run(self, num_users=1000):
        """
        Executes the simulation.
        
        1. Generates users with specific risk profiles.
        2. Simulates 12 months of usage for each user.
        3. Determines which plan offers the lowest cost for the user.
        4. Records the financial outcome for the company based on that choice.
        """
        self.setup_db()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        print(f"Starting simulation for {num_users} users...")
        
        data_rows = []
        
        for user_id in range(1, num_users + 1):
            # 1. Determine User Type & Lambda (Expected visits per month)
            # Distribution: 50% Healthy, 30% Average, 20% Chronic
            rand_val = random.random()
            if rand_val < 0.50:
                user_type = "Healthy"
                lam = 0.2  # ~2-3 visits per year
            elif rand_val < 0.80:
                user_type = "Average"
                lam = 0.6  # ~7-8 visits per year
            else:
                user_type = "Chronic"
                lam = 2.5  # ~30 visits per year
            
            # 2. Simulate 12 Months of Activity & Calculate Plan Costs
            # We calculate the cost for *every* plan to find the best one for the user.
            plan_annual_costs = {p['name']: 0.0 for p in self.plans}
            total_annual_visits = 0
            
            for _ in range(12):
                monthly_visits = self._generate_poisson_visit(lam)
                total_annual_visits += monthly_visits
                
                # Calculate bill for this month for each plan
                for plan in self.plans:
                    # Base Price
                    monthly_bill = plan['price']
                    
                    # Extra Visits Cost
                    if plan['included'] == float('inf'):
                        overage = 0
                    else:
                        overage = max(0, monthly_visits - plan['included'])
                    
                    monthly_bill += (overage * plan['extra'])
                    
                    plan_annual_costs[plan['name']] += monthly_bill

            # 3. User Selection (Rational Actor Model)
            # User chooses the plan with the lowest annual cost
            best_plan_name = min(plan_annual_costs, key=plan_annual_costs.get)
            user_annual_cost = plan_annual_costs[best_plan_name]
            
            # 4. Company Economics
            # Revenue = What user pays
            company_revenue = user_annual_cost
            # Cost = Actual visits * Cost per visit
            company_cost = total_annual_visits * self.cost_per_visit
            # Profit
            company_profit = company_revenue - company_cost
            
            data_rows.append((
                user_id, user_type, total_annual_visits, best_plan_name,
                user_annual_cost, company_revenue, company_cost, company_profit
            ))
            
        c.executemany('''
            INSERT INTO simulation_results 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', data_rows)
        
        conn.commit()
        conn.close()
        print("Simulation completed successfully.")

    def analyze(self):
        """Queries the results and prints a financial report."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        print("\n" + "="*40)
        print("       SIMULATION REPORT")
        print("="*40)
        
        # Overall Metrics
        c.execute('''
            SELECT 
                COUNT(*), 
                SUM(company_profit), 
                AVG(company_profit) 
            FROM simulation_results
        ''')
        total_users, total_profit, avg_profit = c.fetchone()
        
        print(f"Total Users Simulated: {total_users}")
        print(f"Total Annual Profit:   €{total_profit:,.2f}")
        print(f"Avg Profit per User:   €{avg_profit:.2f}")
        
        # Plan Popularity
        print("\n--- Plan Selection Distribution ---")
        c.execute('''
            SELECT chosen_plan, COUNT(*), AVG(company_profit) 
            FROM simulation_results 
            GROUP BY chosen_plan
            ORDER BY COUNT(*) DESC
        ''')
        for row in c.fetchall():
            plan_name, count, plan_avg_profit = row
            print(f"{plan_name:<10}: {count:4d} users selected (Avg Profit: €{plan_avg_profit:.2f})")
            
        # User Type Economics
        print("\n--- Economics by User Type ---")
        c.execute('''
            SELECT user_type, AVG(annual_visits), AVG(company_revenue), AVG(company_profit)
            FROM simulation_results
            GROUP BY user_type
        ''')
        print(f"{'Type':<10} {'Avg Visits':<12} {'Revenue':<10} {'Profit':<10}")
        for row in c.fetchall():
            u_type, visits, rev, prof = row
            print(f"{u_type:<10} {visits:<12.1f} €{rev:<9.1f} €{prof:<9.1f}")
            
        conn.close()

if __name__ == "__main__":
    # Allows running this script directly to test the engine
    sim = SimulationEngine()
    sim.run(num_users=1000)
    sim.analyze()