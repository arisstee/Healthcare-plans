# subscription_simulator.py

# Step 1: Define Plans and Constants

# Dictionary to hold the details of each subscription plan
PLANS = {
    "Lite": {
        "price": 20,
        "included_visits": 2,
        "extra_visit_price": 15
    },
    "Standard": {
        "price": 50,
        "included_visits": 6,
        "extra_visit_price": 10
    },
    "Chronic Care": {
        "price": 90,
        "included_visits": 12,
        "extra_visit_price": 5
    },
    "Unlimited": {
        # Using float('inf') for unlimited visits is a good way to handle this case in code
        "price": 150,
        "included_visits": float('inf'),
        "extra_visit_price": 0
    }
}

# The hospital's internal cost for a single patient visit
HOSPITAL_COST_PER_VISIT = 30 # This is a more realistic cost assumption