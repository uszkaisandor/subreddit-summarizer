#!/usr/bin/env python3

from flask import Flask, render_template, url_for, request, session, redirect
from . import app
import pymongo
import bcrypt
import os
import json


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = os.urandom(24)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY='dev',
    )
    from . import auth
    app.register_blueprint(auth.bp)
    from . import reddit
    app.register_blueprint(reddit.bp)

    app.add_url_rule('/', endpoint='index')
    return app

