""" A small flask Hello World """

import os
import subprocess
import glob

from flask import Flask, request, render_template, send_from_directory, jsonify, redirect

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

def load_all() -> [Song]:
    files = glob.glob("./lyrics/*.json")
    songs = []
    for file in files:
        with open(file, 'r') as fh:
            songs.append(json.loads(fh.read(), object_hook=Song.obj_creator))
    return songs


def addl(lo, lt):
    l = []
    for i in range(0, max(len(lo), len(lt))):
        if i < len(lo):
            l.append(lo[i])
        if i < len(lt):
            l.append(lt[i])
    return l


@APP.route('/static/<path:path>', methods=['GET'])
def _send_static(path):
    return send_from_directory('static', path)


@APP.route('/')
def _index():
    return render_template('home.html', songs=load_all(), commit_hash=COMMIT_HASH)


@APP.route('/search')
def _search():
    return render_template('search.html', \
        songs=addl(genius.search(request.args.get('q')), azlyrics.search(request.args.get('q'))), \
        commit_hash=COMMIT_HASH)


@APP.route('/save')
def _save():
    song_url = request.args.get('q')
    if song_url in [s.url for s in load_all()]:
        return redirect('/lyrics/'+[s for s in load_all() if s.url == song_url][0].id)
    if 'genius.com' in song_url:
        song = genius.download_url(song_url)
    elif 'azlyrics.com' in song_url:
        song = azlyrics.download_url(song_url)
    else:
        return jsonify('unknown, nothing done')
    song.save_to_file()
    return redirect('/lyrics/' + s.id)


@APP.route('/lyrics/<path:path>', methods=['GET'])
def _lyrics_byid(path):
    return jsonify([s for s in load_all() if s.id == path][0].__dict__)


@APP.route('/json/search')
def _json_search():
    # pylint: disable=undefined-variable
    return jsonify([o.__dict__ for o in \
        addl(genius.search(request.args.get('q')), azlyrics.search(request.args.get('q')))])


@APP.route('/json/all')
def _json_all():
    return jsonify([o.__dict__ for o in load_all()])
