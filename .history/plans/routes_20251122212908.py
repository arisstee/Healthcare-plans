from flask import Blueprint, jsonify, request, g
from models.plan import SubscriptionPlan
from models.subscription import UserSubscription
from models import db
from datetime import datetime, timedelta
from auth.routes import auth_required
import numpy as np

plans_bp = Blueprint('plans', __name__)

@plans_bp.route('/plans', methods=['GET'])
def get_plans():
    plans = SubscriptionPlan.query.all()
    return jsonify([{ 
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'included_visits': "Unlimited" if p.included_visits == -1 else p.included_visits,
        'extra_visit_price': p.extra_visit_price,
        'features': p.features 
    } for p in plans])

@plans_bp.route('/subscribe', methods=['POST'])
@auth_required
def subscribe():
    data = request.get_json()
    plan_id = data.get('plan_id')
    months = data.get('months', 1)
    
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
    return jsonify({'message': f'Subscribed to {plan.name} for {months} months.'})

@plans_bp.route('/simulation/profit', methods=['GET'])
@auth_required
def simulate_profit():
    subs = UserSubscription.query.filter_by(active=True).all()
    
    if not subs:
        return jsonify({'message': 'No active subscriptions to simulate.'}), 200

    total_revenue = 0
    total_cost = 0
    results = []
    HOSPITAL_COST_PER_VISIT = 30
    
    for sub in subs:
        avg_visits = np.random.randint(1, 8) 
        simulated_visits = np.random.poisson(lam=avg_visits)
        
        plan = sub.plan
        
        if plan.included_visits == -1: 
            extra_visits = 0
        else:
            extra_visits = max(0, simulated_visits - plan.included_visits)
            
        revenue = plan.price + (extra_visits * plan.extra_visit_price)
        cost = simulated_visits * HOSPITAL_COST_PER_VISIT
        profit = revenue - cost
        
        total_revenue += revenue
        total_cost += cost
        
        results.append({
            "user_id": sub.user_id,
            "plan": plan.name,
            "simulated_visits": int(simulated_visits),
            "revenue": revenue,
            "cost": cost,
            "profit": profit
        })

    return jsonify({
        "simulation_summary": {
            "total_users": len(subs),
            "total_net_profit": total_revenue - total_cost
        },
        "details": results
    })