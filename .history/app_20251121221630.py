import click
from flask import Flask
from models import db
from auth.routes import auth_bp
from plans.routes import plans_bp
from simulation.engine import SimulationEngine  # Import our new engine

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize Database
db.init_app(app)

# Register Blueprints (Routes)
app.register_blueprint(auth_bp)
app.register_blueprint(plans_bp)

# --- CUSTOM CLI COMMANDS ---
@app.cli.command("run-simulation")
@click.option('--users', default=1000, help='Number of users to simulate')
def run_simulation_command(users):
    """
    Runs the healthcare subscription simulation from the command line.
    Usage: flask run-simulation --users 500
    """
    print(f"Initializing simulation for {users} users...")
    engine = SimulationEngine()
    engine.run(num_users=users)
    engine.analyze()

# --- MAIN ENTRY POINT ---
if __name__ == "__main__":
    # Create tables for the web app (users, plans) if they don't exist
    with app.app_context():
        db.create_all()
    
    # Run the web server
    app.run(debug=True)