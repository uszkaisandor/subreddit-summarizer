from flask import (
    Blueprint, redirect, render_template, request, session, url_for
)
import pymongo

from . import reddit
bp = Blueprint('reddit', __name__, url_prefix='/reddit')


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
        if not new_subreddit == '':
            users.update_one({'username': session['username']}, {'$push': {'subreddits': new_subreddit} })
        return render_template('reddit.html')

