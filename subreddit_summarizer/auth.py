
from flask import (
    Blueprint, redirect, render_template,
    request, session, url_for, current_app
)
import pymongo
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('auth', __name__, url_prefix='/')

""" Connect to MongoDB """
conn = pymongo.MongoClient()    # connect to localhost
db = conn['redditclient']    # select database
users = db['users']   # select users collection
subreddits = db['subreddits']


""" App entry """
@bp.route('/')
def index():
    if 'username' in session:
        user = session['username']
        return redirect(url_for('reddit.get_reddit'))
    return render_template('index.html')


""" Register """
@bp.route('/register', methods=['POST', 'GET'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username:
            error = 'Username is required.'
        elif not password or len(password) < 8:
            error = 'Password is required (8 characters min).'
        elif db.users.find_one({'username': username}):
            error = 'The username "{}" already exists!'.format(username)
        if error is None:
            password_hash = generate_password_hash(password)
            db.users.insert_one(
                {'username': username, 'password': password_hash, 'subreddits': [], 'posts': []})
            return redirect(url_for('index'))
    return render_template('register.html', error=error)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.users.find_one({'username': request.form['username']})

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['username'] = user['username']
            return redirect(url_for('index'))

    return render_template('index.html', error=error)


@bp.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('index'))

@bp.route('/delete_user', methods=['POST'])
def delete_user():
    if request.method == 'POST':
        db.users.delete_one({"username" : session['username']})
        session.clear()
        return redirect(url_for('index'))

