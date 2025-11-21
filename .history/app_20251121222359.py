from flask import Flask
from models import db
from auth.routes import auth_bp
from plans.routes import plans_bp

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(plans_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
