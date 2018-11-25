from setuptools import setup

setup(
    name='subreddit_summarizer',
    packages=['subreddit_summarizer'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)