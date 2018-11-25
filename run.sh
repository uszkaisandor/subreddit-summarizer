#!/bin/bash

export FLASK_APP='subreddit_summarizer/app.py'
export FLASK_ENV=development
export FLASK_DEBUG=True
flask run
