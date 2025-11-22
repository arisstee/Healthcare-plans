from . import db

class SubscriptionPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    # included_visits: -1 denotes "Unlimited"
    included_visits = db.Column(db.Integer, nullable=False)
    extra_visit_price = db.Column(db.Float, nullable=False)
    features = db.Column(db.Text)