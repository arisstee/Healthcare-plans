from flask import Flask
from models import db
from auth.routes import auth_bp
from plans.routes import plans_bp
from models.plan import SubscriptionPlan

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize extensions
db.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(plans_bp)

def seed_plans():
    """Seeds the database with the plans defined in the project PDF."""
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
            included_visits=-1,  # -1 represents Unlimited in our logic
            extra_visit_price=0, 
            features="Unlimited doctor consultations, Yearly medical check-up, Specialist referrals included"
        )
    ]
    db.session.bulk_save_objects(plans)
    db.session.commit()
    print("Database seeded with subscription plans.")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_plans()
    app.run(debug=True)