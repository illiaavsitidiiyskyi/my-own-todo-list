from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import User
import hashlib

auth_bp = Blueprint('auth', __name__, template_folder='templates')


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(password, hashed):
    return hash_password(password) == hashed


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Перевірка чи існує користувач
        if User.select().where(User.username == username).exists():
            flash('A user with that name already exists', 'danger')
            return redirect(url_for('auth.register'))

        # Створення нового користувача
        User.create(username=username, password=hash_password(password))
        flash('Registration is successful! Sign in', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            user = User.get(User.username == username)
            if check_password(password, user.password):
                session['user_id'] = user.id
                session['username'] = user.username
                return redirect(url_for('todo.index'))
            else:
                flash('Invalid password', 'danger')
        except User.DoesNotExist:
            flash('No user found', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You are logged out', 'success')
    return redirect(url_for('auth.login'))