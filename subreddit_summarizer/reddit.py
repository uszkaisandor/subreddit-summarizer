from flask import (
    Blueprint, redirect, render_template, request, session, url_for
)
import pymongo
import json
import requests
from . import reddit
from flask import current_app
bp = Blueprint('reddit', __name__, url_prefix='/reddit')


def new_subreddit(response, subreddit):
    conn = pymongo.MongoClient()    # connect to localhost
    db = conn['redditclient']    # select database
    users = db['users']   # select users collection
    #Alert user, that subreddit already exists
    cursor = users.find_one({'username': session['username'], 'subreddits': {"$in": [subreddit]}})
    current_app.logger.info(cursor)
    if cursor is None:
        users.update_one({'username': session['username']}, {'$push': {'subreddits': subreddit}})
        for item in response['data']['children']:
        # If post already exists:
        #cursor2 = users.find_one({'username': session['username'], 'posts': {"$in": {'_id': }}})
        #users.update_one({'username': session['username']})
        #else:
            item['_id'] = item['data']['name']
            users.update_one({'username': session['username']}, {'$push': {'posts': item}})
        context = {
            'mode': 'success',
            'message': 'Subreddit successfully added!'
        }
        return context
    return {'mode': 'error', 'message': 'Subreddit already exists!'}

def get_post(subreddit):
    # User agent
    url = "http://www.reddit.com/r/{}/.json".format(subreddit)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(url, headers=headers).json()
    # If there is no such subreddit
    if not 'data' in response or response['data']['dist'] == 0:
        context = {
            'mode': 'error',
            'message': 'No such subreddit!'
        }
        return context
    else:
        return new_subreddit(response, subreddit)


@bp.route('', methods=['POST', 'GET'])
def get_reddit():
    if request.method in ['POST', 'GET']:
        return render_template('reddit.html', username=session['username'])


@bp.route('/mysubreddits', methods=['POST'])
def list_my_subreddits():
    if request.method == 'POST':
        conn = pymongo.MongoClient()    # connect to localhost
        db = conn['redditclient']    # select database
        users = db['users']   # select users collection
        actual_user_subreddits = users.find_one(
            {'username': session['username']}, {'_id': 0, 'subreddits': 1})
        # TODO: Serialize actual_user_subreddits to python object
        return render_template('reddit.html',
                               subreddits=actual_user_subreddits)


@bp.route('/addsubreddit', methods=['GET', 'POST'])
def add_subreddit():
    conn = pymongo.MongoClient()    # connect to localhost
    db = conn['redditclient']    # select database
    users = db['users']   # select users collection
    new_subreddit = request.args.get('subreddit', '').strip()
    context = get_post(new_subreddit)
    return render_template('reddit.html', **context)
