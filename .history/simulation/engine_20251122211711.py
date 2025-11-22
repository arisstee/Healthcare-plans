import sqlite3
import random
import math

# Try to import numpy for efficient Poisson distribution, fallback if missing
try:
    import numpy as np
    USE_NUMPY = True
except ImportError:
    USE_NUMPY = False

class SimulationEngine:
    """
    Handles the 'Module 6' requirements:
    - Simulate User Data (Random Variables).
    - Model Usage (Poisson Distribution).
    - Store results in SQLite.
    - Compare pricing strategies.
    """

    def __init__(self, db_path='healthcare_simulation.db'):
        self.db_path = db_path
        self.cost_per_visit = 30  # Hospital internal cost per visit
        
        # Plans defined in the PDF
        self.plans = [
            {"name": "Lite Plan", "price": 20, "included": 2, "extra": 15},
            {"name": "Standard Plan", "price": 50, "included": 6, "extra": 10},
            {"name": "Chronic Care Plan", "price": 90, "included": 12, "extra": 5},
            {"name": "Unlimited Plan", "price": 150, "included": float('inf'), "extra": 0}
        ]

    def _generate_poisson_visit(self, lam):
        """Generate a single month's visit count based on Lambda."""
        if USE_NUMPY:
            return np.random.poisson(lam)
        else:
            # Fallback algorithm if numpy is not installed
            L = math.exp(-lam)
            k = 0
            p = 1.0
            while p > L:
                k += 1
                p *= random.random()
            return k - 1

    def setup_db(self):
        """Initialize the separate simulation database table."""
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
        """Runs the simulation loop."""
        self.setup_db()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        data_rows = []
        
        for user_id in range(1, num_users + 1):
           # 1. Identify User Type (Random Variable)
            rand_val = random.random()
            if rand_val < 0.50:
                user_type = "Healthy"
                # INCREASED: Occasional visits
                lam = 1.0  
            elif rand_val < 0.80:
                user_type = "Average"
                # INCREASED: Now ~5 visits/month (Makes them want Standard Plan)
                lam = 5.0  
            else:
                user_type = "Chronic"
                # INCREASED: Now ~12 visits/month (Makes them want Chronic Plan)
                lam = 12.0
            
            # 2. Simulate 12 Months of Usage
            plan_annual_costs = {p['name']: 0.0 for p in self.plans}
            total_annual_visits = 0
            
            for _ in range(12):
                monthly_visits = self._generate_poisson_visit(lam)
                total_annual_visits += monthly_visits
                
                # Calculate potential bill for ALL plans to find the best one
                for plan in self.plans:
                    monthly_bill = plan['price']
                    if plan['included'] == float('inf'):
                        overage = 0
                    else:
                        overage = max(0, monthly_visits - plan['included'])
                    monthly_bill += (overage * plan['extra'])
                    plan_annual_costs[plan['name']] += monthly_bill

            # 3. Rational Choice: User picks the cheapest plan for their usage
            best_plan_name = min(plan_annual_costs, key=plan_annual_costs.get)
            user_annual_cost = plan_annual_costs[best_plan_name]
            
            # 4. Compute Economics
            company_revenue = user_annual_cost
            company_cost = total_annual_visits * self.cost_per_visit
            company_profit = company_revenue - company_cost
            
            data_rows.append((
                user_id, user_type, total_annual_visits, best_plan_name,
                user_annual_cost, company_revenue, company_cost, company_profit
            ))
            
        c.executemany('INSERT INTO simulation_results VALUES (?, ?, ?, ?, ?, ?, ?, ?)', data_rows)
        conn.commit()
        conn.close()

    def analyze(self):
        """Prints the analysis/summary."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        print("\n" + "="*30)
        print("   SIMULATION RESULTS")
        print("="*30)
        
        # Total Profit
        c.execute('SELECT SUM(company_profit) FROM simulation_results')
        total_profit = c.fetchone()[0]
        print(f"Total Annual Profit: €{total_profit:,.2f}")
        
        # Plan Distribution
        print("\n--- Plan Selection by Users ---")
        c.execute('SELECT chosen_plan, COUNT(*) FROM simulation_results GROUP BY chosen_plan ORDER BY COUNT(*) DESC')
        for row in c.fetchall():
            print(f"{row[0]:<20}: {row[1]} Users")
            
        conn.close()