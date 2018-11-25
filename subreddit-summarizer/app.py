#!/usr/bin/env python3

from flask import Flask, render_template, url_for, request, session, redirect
import pymongo
import bcrypt
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

""" Connect to MongoDB """
conn = pymongo.MongoClient()    # connect to localhost
db = conn['redditclient']    # select database
users = db['users']   # select users collection
subreddits = db['subreddits']


def username_is_not_valid(username):
    if len(username) < 4:
        return 'The minimum length of a username is 4 characters!'
    if db.users.find_one({'username' : username}):
        return 'The username "{}" already exists!'.format(username)
    return ''


def password_is_valid(pw):
    if len(pw) < 8:
        return False
    return True


""" TODO """
def get_subreddits():
    #get https://www.reddit.com/api/r/python/.json
    return ""


""" App entry """
@app.route('/')
def index():
    if 'username' in session:
        user = session['username']
        return render_template('reddit_posts.html', username=user)
    return render_template('index.html')


""" Login """
@app.route('/login', methods=['POST'])
def login():
    login_user = db.users.find_one({'username': request.form['username']})
    if login_user:
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), login_user['password']):
            app.logger.info("Passwords are same")
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    error = 'Invalid username or password'
    return render_template('index.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


""" Register """
@app.route('/register', methods=['POST', 'GET'])
def register():
    error=''
    if request.method == 'POST':
        if username_is_not_valid(request.form['username']):
                return render_template('register.html', error=username_is_not_valid(request.form['username']))        
        new_password = request.form['password']
        if password_is_valid(new_password):
            hashpass = bcrypt.hashpw(request.form['username'].encode('utf-8'), bcrypt.gensalt())
            db.users.insert_one({'username': request.form['username'], 'password': hashpass, 'subreddits': []})
            #session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            error = "The minimum length of a password is 8 characters!"
    return render_template('register.html', error=error)

#######################################
if __name__ == '__main__':
    app.run(debug=True)