from . import db

class SubscriptionPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    included_visits = db.Column(db.Integer, nullable=True)  # None or int
    extra_visit_price = db.Column(db.Float, nullable=True)
    features = db.Column(db.Text)