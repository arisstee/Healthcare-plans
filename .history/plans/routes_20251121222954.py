# plans/routes.py
from flask import Blueprint, jsonify, request, g
from models.plan import SubscriptionPlan
from models.subscription import UserSubscription
from models import db
from datetime import datetime, timedelta
from auth.routes import auth_required

plans_bp = Blueprint('plans', __name__)

@plans_bp.route('/plans', methods=['GET'])
def get_plans():
    plans = SubscriptionPlan.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'included_visits': p.included_visits,
        'extra_visit_price': p.extra_visit_price,
        'features': p.features
    } for p in plans])

@plans_bp.route('/subscribe', methods=['POST'])
@auth_required
def subscribe():
    plan_id = request.json.get('plan_id')
    months = request.json.get('months', 1)
    plan = SubscriptionPlan.query.get(plan_id)
    if not plan:
        return jsonify({'message': 'Plan not found'}), 404
    user_id = g.user_id
    now = datetime.utcnow()
    subscription = UserSubscription(
        user_id=user_id,
        plan_id=plan_id,
        start_date=now,
        end_date=now + timedelta(days=30*months),
        active=True
    )
    db.session.add(subscription)
    db.session.commit()
    return jsonify({'message': 'Subscription created.'})

@plans_bp.route('/profit', methods=['GET'])
@auth_required
def profit():
    subs = UserSubscription.query.filter_by(active=True).all()
    months = 1
    cost_per_visit = 10

    total_revenue = sum(sub.plan.price for sub in subs) * months
    # Assume each subscription maxes included visits per month
    total_visits = sum((sub.plan.included_visits or 0) * months for sub in subs)
    total_cost = total_visits * cost_per_visit
    total_profit = total_revenue - total_cost

    return jsonify({
        "revenue": total_revenue,
        "cost": total_cost,
        "profit": total_profit
    })
