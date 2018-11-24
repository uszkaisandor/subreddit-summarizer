#!/usr/bin/env python3

from flask import Flask, render_template, url_for, request, session, redirect
import pymongo
import bcrypt
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

conn = pymongo.MongoClient()    # connect to localhost
db = conn['redditclient']    # select database
users = db['users']   # select users collection
subreddits = db['subreddits']

""" App entry """
@app.route('/')
def index():
    if 'username' in session:
        return 'You are logged in as {}'.format(session['username'])
    return render_template('index.html')


@app.route('/login', methods = ['POST'])
def login():
    login_user = db.users.find_one({'username': request.form['username']})
    if login_user:
        if bcrypt.checkpw(request.form['pass'].encode('utf-8'), login_user['password']):
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    return 'Invalid username or password'

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        existing_user = db.users.find_one({'username' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            db.users.insert_one({'username': request.form['username'], 'password': hashpass, 'subreddits': []})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        return 'That username already exists!'
    
    return render_template('register.html')



#######################################
if __name__ == '__main__':
    app.run(debug=True)