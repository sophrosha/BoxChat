# Authentication routes

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models import User
import re

auth_bp = Blueprint('auth', __name__)

def get_client_ip():
    # Safely get client IP address
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

def validate_username(username):
    # Validate username format and length
    if not username or len(username) < 3:
        return False, "user name should be at least 3 characters long"
    
    if len(username) > 30:
        return False, "user name should be less than 30 characters long"
    
    # Only alphanumeric, hyphens, underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "user name can only contain letters, numbers, hyphens, and underscores"
    
    return True, ""

def validate_password(password):
    # Validate password strength
    if not password or len(password) < 8:
        return False, "password should be at least 8 characters long"
    
    if len(password) > 100:
        return False, "password should be less than 100 characters long"
    
    # Check for at least one uppercase, one lowercase, one digit
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()-_=+[]{}|;:,.<>?' for c in password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "password should contain at least one uppercase letter, one lowercase letter, and one digit"
    
    return True, ""

def is_ip_banned(ip):
    # Check if IP is in banned list
    banned_users = User.query.filter_by(is_banned=True).all()
    for user in banned_users:
        if user.banned_ips:
            ips = [ip_addr.strip() for ip_addr in user.banned_ips.split(',') if ip_addr.strip()]
            if ip in ips:
                return True
    return False

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Login page and handler
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        client_ip = get_client_ip()
        
        # Check if IP is banned
        if is_ip_banned(client_ip):
            flash('your IP address is banned')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and is not banned
        if user and user.is_banned:
            flash(f'account banned. reason: {user.ban_reason or "not specified"}')
            return render_template('login.html')
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        
        flash('login failed. check your username and password')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Registration page and handler with security checks
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        client_ip = get_client_ip()
        
        # Check if IP is banned
        if is_ip_banned(client_ip):
            flash('your IP address is banned and cannot create new accounts')
            return render_template('register.html')
        
        # Validate username
        is_valid, msg = validate_username(username)
        if not is_valid:
            flash(msg)
            return render_template('register.html')
        
        # Validate password
        is_valid, msg = validate_password(password)
        if not is_valid:
            flash(msg)
            return render_template('register.html')
        
        # Check password confirmation
        if password != confirm_password:
            flash('passwords do not match')
            return render_template('register.html')
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('username already taken')
            return render_template('register.html')
        
        # Check for multiple accounts from same IP (rate limiting)
        # Allow only 3 accounts per IP per day
        from datetime import timedelta
        from sqlalchemy import and_
        
        # Note: This is simplified. For production, consider using Redis for rate limiting
        # For now, just create the account
        
        new_user = User(
            username=username,
            password=generate_password_hash(password, method='scrypt')
        )
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        flash('account created successfully')
        return redirect(url_for('main.dashboard'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    # Logout handler
    logout_user()
    return redirect(url_for('auth.login'))
