from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user
from src.models import User, db
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'status': 'error',
            'error': {
                'code': 'USER_EXISTS',
                'message': 'Email already registered'
            }
        }), 400
        
    user = User(
        username=data['username'],
        email=data['email'],
        organization=data.get('organization', '')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'User registered successfully',
        'data': {
            'user_id': user.id,
            'username': user.username
        }
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        login_user(user)
        user.update_last_login()
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'data': {
                'token': 'test-token',  # Replace with real token generation
                'user_id': user.id,
                'username': user.username
            }
        }), 200
    
    return jsonify({
        'status': 'error',
        'error': {
            'code': 'INVALID_CREDENTIALS',
            'message': 'Invalid email or password'
        }
    }), 401
