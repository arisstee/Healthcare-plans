import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///healthcare.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # In production, use a secure random key
    JWT_SECRET = os.environ.get('JWT_SECRET', 'super-secret-key-change-me')