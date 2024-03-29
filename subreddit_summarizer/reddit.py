from flask import (
    Blueprint, redirect, render_template, request, session, url_for
)
from . import reddit
from flask import current_app
from datetime import datetime
import pymongo
import json
import requests
import pytz

bp = Blueprint('reddit', __name__, url_prefix='/reddit')


def time_from_int(unix_time):
    timestamp = datetime.utcfromtimestamp(unix_time)
    old_timezone = pytz.timezone("UTC")
    new_timezone = pytz.timezone("Europe/Budapest")
    # returns datetime in the new timezone
    timestamp_in_new_timezone = old_timezone.localize(
        timestamp).astimezone(new_timezone)
    return timestamp_in_new_timezone.strftime('%Y-%m-%d %H:%M')


def new_subreddit(response, subreddit):
    conn = pymongo.MongoClient()    # connect to localhost
    db = conn['redditclient']    # select database
    users = db['users']   # select users collection
    cursor = users.find_one(
        {'username': session['username'], 'subreddits': {"$in": [subreddit]}})

    # Subreddit doesn't exist in the database yet.
    if cursor is None:
        users.update_one({'username': session['username']}, {
                         '$push': {'subreddits': subreddit}})
        for item in response['data']['children']:
            item['_id'] = item['data']['id']
            item['data']['created'] = time_from_int(item['data']['created'])
            users.update_one({'username': session['username']}, {
                             '$push': {'posts': item}})
        context = {
            'mode': 'success',
            'message': 'Subreddit successfully added!'
        }
        return context
    # Subreddit already exists
    return {'mode': 'error', 'message': 'Subreddit already exists!'}


def update_all_posts():
    conn = pymongo.MongoClient()    # connect to localhost
    db = conn['redditclient']    # select database
    users = db['users']   # select users collection
    cursor_subred = users.find_one(
        {'username': session['username']}, {'_id': 0, 'subreddits': 1})
    if len(cursor_subred['subreddits']) > 0:
        users.update_one({'username': session['username']}, {
                         '$unset': {'posts': 1}})
    for subred in cursor_subred['subreddits']:
        # User agent
        url = "http://www.reddit.com/r/{}/.json".format(subred)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        response = requests.get(url, headers=headers).json()
        for item in response['data']['children']:
            item['_id'] = item['data']['id']
            item['data']['created'] = time_from_int(item['data']['created'])
            users.update_one({'username': session['username']}, {
                             '$push': {'posts': item}}, upsert=True)


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
        # TODO: Display posts
        conn = pymongo.MongoClient()    # connect to localhost
        db = conn['redditclient']    # select database
        users = db['users']   # select users collection
        update_all_posts()
        cursor = users.find_one({'username': session['username']}, {
                                '_id': 0, 'posts': 1})
        # Sort posts by reddit score
        sorted_by_score = sorted(cursor['posts'], key=lambda i: i['data']
                                 ['score'], reverse=True)
        cursor['posts'] = sorted_by_score
        return render_template('reddit.html', username=session['username'], **cursor)


@bp.route('/mysubreddits', methods=['POST', 'GET'])
def list_my_subreddits():
    if request.method in ['POST', 'GET']:
        conn = pymongo.MongoClient()    # connect to localhost
        db = conn['redditclient']    # select database
        users = db['users']   # select users collection
        actual_user_subreddits = users.find_one(
            {'username': session['username']}, {'_id': 0, 'subreddits': 1})
        warning = None
        if actual_user_subreddits['subreddits'] == []:
            warning = "There are no subreddits yet."
        # TODO: Serialize actual_user_subreddits to python object
        return render_template('reddit.html',
                               subreddits=actual_user_subreddits, warning=warning)


@bp.route('/addsubreddit', methods=['GET', 'POST'])
def add_subreddit():
    conn = pymongo.MongoClient()    # connect to localhost
    db = conn['redditclient']    # select database
    users = db['users']   # select users collection
    new_subreddit = request.args.get('subreddit', '').strip()
    context = get_post(new_subreddit)
    return render_template('reddit.html', **context)


@bp.route('/delete_subreddit/<subred_name>', methods=['POST', 'GET'])
def delete_subreddit(subred_name):
    conn = pymongo.MongoClient()    # connect to localhost
    db = conn['redditclient']    # select database
    users = db['users']   # select users collection
    users.update_one({'username': session['username']}, {
                         '$pull': {'subreddits': subred_name}})
    return redirect(url_for('reddit.list_my_subreddits'))