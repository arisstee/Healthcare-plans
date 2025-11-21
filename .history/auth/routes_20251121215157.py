import bcrypt
import jwt
import datetime
from flask import Blueprint, request, jsonify, make_response, current_app, g
from models.user import User
from models import db

auth_bp = Blueprint('auth', __name__)

def encode_jwt(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')
    return token

def decode_jwt(token):
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def auth_required(func):
    def wrapper(*args, **kwargs):
        token = request.cookies.get('jwt')
        payload = decode_jwt(token) if token else None
        if not payload or not payload.get('user_id'):
            return jsonify({'message': 'Token invalid or missing'}), 401
        g.user_id = payload['user_id']
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = User(username=username, password=hashed)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password):
        return jsonify({'message': 'Invalid username or password'}), 401
    token = encode_jwt(user.id)
    resp = make_response({'message': 'Login successful'})
    resp.set_cookie('jwt', token, httponly=True, samesite='Strict')
    return resp

@auth_bp.route('/logout', methods=['POST'])
def logout():
    resp = make_response(jsonify({'message': 'Logged out'}))
    resp.set_cookie('jwt', '', expires=0, httponly=True, samesite='Strict')
    return resp
