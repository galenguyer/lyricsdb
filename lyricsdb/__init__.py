""" A small flask Hello World """

import os
import subprocess

from flask import Flask, request, render_template, send_from_directory, jsonify

from .azlyrics import *
from .genius import *

APP = Flask(__name__)

# Load file based configuration overrides if present
if os.path.exists(os.path.join(os.getcwd(), 'config.py')):
    APP.config.from_pyfile(os.path.join(os.getcwd(), 'config.py'))
else:
    APP.config.from_pyfile(os.path.join(os.getcwd(), 'config.env.py'))

APP.secret_key = APP.config['SECRET_KEY']

COMMIT_HASH = None
try:
    COMMIT_HASH = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']) \
                            .strip() \
                            .decode('utf-8')
# pylint: disable=bare-except
except:
    COMMIT_HASH = None

@APP.route('/static/<path:path>', methods=['GET'])
def _send_static(path):
    return send_from_directory('static', path)

@APP.route('/')
def _index():
    return render_template('home.html', commit_hash=COMMIT_HASH)


@APP.route('/search')
def _search():
    # pylint: disable=undefined-variable
    return jsonify([o.__dict__ for o in \
        genius.search(request.args.get('q')) + azlyrics.search(request.args.get('q'))])
