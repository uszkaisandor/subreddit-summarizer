from flask import (
    Blueprint, redirect, render_template, request, session, url_for
)
import pymongo
import json
import requests
from . import reddit
bp = Blueprint('reddit', __name__, url_prefix='/reddit')


def get_post(subreddit):
    # User agent
    url="http://www.reddit.com/r/{}/.json".format(subreddit)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(url, headers=headers).json()
    # If there is no such subreddit
    if response['data']['dist'] == 0:
        return None
    else:
        conn = pymongo.MongoClient()    # connect to localhost
        db = conn['redditclient']    # select database
        users = db['users']   # select users collection
        users.update_one({'username': session['username']}, {'$push': {'subreddits': subreddit} })
        for item in response['data']['children']:
            pass
            
@bp.route('', methods=['POST', 'GET'])
def get_reddit():
    if request.method in ['POST','GET']:
        return render_template('reddit.html', username=session['username'])


@bp.route('/mysubreddits', methods=['POST'])
def list_my_subreddits():
    if request.method == 'POST':
        conn = pymongo.MongoClient()    # connect to localhost
        db = conn['redditclient']    # select database
        users = db['users']   # select users collection
        actual_user_subreddits = users.find_one({'username': session['username']}, {'_id': 0, 'subreddits': 1})
        #TODO: Serialize actual_user_subreddits to python object
        return render_template('reddit.html',
                               subreddits=actual_user_subreddits)

@bp.route('/addsubreddit', methods=['GET'])
def add_subreddit():
    if request.method == 'GET':
        conn = pymongo.MongoClient()    # connect to localhost
        db = conn['redditclient']    # select database
        users = db['users']   # select users collection
        new_subreddit = request.args.get('subreddit', '').strip()
        # TODO: Handle when there isn't a subreddit with this name...

        get_post(new_subreddit)

        #if not new_subreddit == '':
        #    users.update_one({'username': session['username']}, {'$push': {'subreddits': new_subreddit} })
        return render_template('reddit.html')

