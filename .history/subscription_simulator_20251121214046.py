from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscriptions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    usage_gb = db.Column(db.Float, nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'))

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    gb_limit = db.Column(db.Float, nullable=True)  # For tiered plans, etc.

def simulate_users(n=100):
    users = []
    for i in range(n):
        usage_gb = np.random.poisson(10)  # Adjust mean as needed
        users.append(User(name=f"User{i}", usage_gb=usage_gb, plan_id=None))
    return users

def assign_plans(users, plans):
    for user in users:
        plan = random.choice(plans)
        user.plan_id = plan.id

def setup():
    db.drop_all()
    db.create_all()
    plans = [
        Plan(name='Flat Rate', price=20, gb_limit=None),
        Plan(name='Tiered 10GB', price=10, gb_limit=10),
        Plan(name='Pay Per Use', price=2, gb_limit=1)  # $2 per GB over cap
    ]
    db.session.add_all(plans)
    db.session.commit()
    users = simulate_users()
    assign_plans(users, plans)
    db.session.add_all(users)
    db.session.commit()

@app.route("/")
def index():
    return "Subscription Simulator is running. Visit /results to see the analysis."

@app.route("/results")
def results():
    users = User.query.all()
    plans = Plan.query.all()
    outcome = []
    for plan in plans:
        plan_users = [u for u in users if u.plan_id == plan.id]
        total_revenue = 0
        total_cost = 0
        for u in plan_users:
            if plan.name == "Flat Rate":
                revenue = plan.price
            elif plan.name == "Tiered 10GB":
                if u.usage_gb <= 10:
                    revenue = plan.price
                else:
                    revenue = plan.price + 2 * (u.usage_gb - 10)
            else:  # Pay Per Use
                revenue = plan.price * u.usage_gb

            cost = 5 + 0.5 * u.usage_gb
            total_revenue += revenue
            total_cost += cost
        n = len(plan_users) if plan_users else 1
        outcome.append({
            "plan": plan.name,
            "users": n,
            "avg expected revenue": total_revenue / n,
            "avg expected cost": total_cost / n,
            "expected profit": (total_revenue - total_cost) / n
        })
    return jsonify(outcome)

if __name__ == "__main__":
    with app.app_context():
        setup()
    app.run(debug=True)
