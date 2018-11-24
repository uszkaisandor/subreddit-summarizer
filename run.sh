#!/bin/bash

export FLASK_APP="subreddit-summarizer/app.py"
export FLASK_ENVIRONMENT="DEV"
export FLASK_DEBUG=true
flask run