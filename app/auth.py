import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, sessions
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app as app
from app.models import User
from app import db

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        age = request.form['age']
        gender = request.form['gender']
        if age:
            age = int(age)
        error = None
        print("form received")

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'

        user = User.query.filter_by(email=email).first()
        if user:
            error = 'Email {} already exists'.format(email)

        if error is None:
            user = User(username=username, password=password, email=email, age=age, gender=gender)
            db.session.add(user)
            db.session.commit()

            session['username'] = username
            print("user added")
            return redirect(url_for('auth_bp.login'))
        flash(error)

    return render_template('register.html')


@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        user = User.query.filter_by(email=email).first()

        if user is None:
            error = 'Incorrect email.'
        elif password != user.password:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['email'] = email
            load_logged_in_user()
            print('logging user')
            return redirect(url_for('profile_bp.home'))

        flash(error)

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('market_bp.index'))


@auth_bp.before_app_request
def load_logged_in_user():
    email = session.get('email')

    if email is None:
        g.user = None
    else:
        g.user = User.query.filter_by(email=email).first()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth_bp.login'))
        return view(**kwargs)
    return wrapped_view


def get_user(email):
    try:
        user = User.query.filter_by(email=email).first()
    except:
        return 'No associated user found'

    return user
