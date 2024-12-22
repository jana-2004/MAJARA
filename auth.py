import os
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager,create_access_token
from app import jwt,app
from flask import jsonify

load_dotenv()
app.config['JWT_SECRET_KEY']= os.environ.get('JWT_SECRET_KEY')   # used to hash the token

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "message": "The token has expired",
        "error": "token_expired"
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        "message": "Signature verification failed",
        "error": "invalid_token"
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "message": "Request does not contain an access token",
        "error": "authorization_required"
    }), 401