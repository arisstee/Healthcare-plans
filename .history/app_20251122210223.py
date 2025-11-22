import click
from flask import Flask
from models import db
from auth.routes import auth_bp
from plans.routes import plans_bp
from models.plan import SubscriptionPlan
from simulation.engine import SimulationEngine

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize Database
db.init_app(app)

# Register Routes
app.register_blueprint(auth_bp)
app.register_blueprint(plans_bp)

def seed_plans():
    """Seeds the database with the specific plans from the PDF."""
    if SubscriptionPlan.query.first():
        return
    
    plans = [
        SubscriptionPlan(
            name="Lite Plan", 
            price=20, 
            included_visits=2, 
            extra_visit_price=15, 
            features="Basic doctor consultations, Blood pressure check, Basic blood test"
        ),
        SubscriptionPlan(
            name="Standard Plan", 
            price=50, 
            included_visits=6, 
            extra_visit_price=10, 
            features="Doctor consultations, X-ray once per year, Basic diagnostic tests"
        ),
        SubscriptionPlan(
            name="Chronic Care Plan", 
            price=90, 
            included_visits=12, 
            extra_visit_price=5, 
            features="Priority doctor access, Monthly blood tests, Chronic disease monitoring"
        ),
        SubscriptionPlan(
            name="Unlimited Plan", 
            price=150, 
            included_visits=-1,  # -1 represents Unlimited
            extra_visit_price=0, 
            features="Unlimited doctor consultations, Yearly medical check-up, Specialist referrals included"
        )
    ]
    db.session.bulk_save_objects(plans)
    db.session.commit()
    print("Database seeded with subscription plans.")

# --- CLI COMMAND FOR MODULE 6 SIMULATION ---
@app.cli.command("run-simulation")
@click.option('--users', default=1000, help='Number of users to simulate')
def run_simulation_command(users):
    """
    Runs the simulation for 1000 users (Module 6 Requirement).
    Command: flask run-simulation
    """
    print(f"Initializing simulation for {users} synthetic users...")
    engine = SimulationEngine()
    engine.run(num_users=users)
    engine.analyze()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_plans()
    app.run(debug=True)