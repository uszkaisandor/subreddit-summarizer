from flask import (
    Blueprint, redirect, render_template, request, session, url_for
)
import pymongo
bp = Blueprint('reddit', __name__, url_prefix='/reddit')

@bp.route('/reddit')
def get_reddit():
    conn = pymongo.MongoClient()    # connect to localhost
    db = conn['redditclient']    # select database
    users = db['users']   # select users collection
    return render_template('posts.html', username="Sanyi")
