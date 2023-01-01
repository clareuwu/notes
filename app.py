import sqlite3
from datetime import datetime
import bcrypt
from flask import Flask, render_template, request, redirect, abort, session
from models import User, Deck, Card, Deck_Cards

app = Flask(__name__, template_folder='s/t', static_folder='s')
app.secret_key=b'245d0a327be38b04440549727c6a1d06904ed6262e50024359847adef2e97423'
db = sqlite3.connect('app.db', check_same_thread=False)
db.execute('PRAGMA foreign_keys = 1')

def hash_pass(password: str) -> bytes:
    """Hash password w bcrypt, return hashed in bytes"""
    return bcrypt.hashpw(bytes(password, 'UTF-8'), bcrypt.gensalt())

def match_pass(password: str, hashed: bytes) -> bool:
    """Check if pw matches hashed password"""
    return bcrypt.checkpw(password.encode('UTF-8'), hashed)

def create_user(username: str, password: str) -> bool:
    """Create user in DB"""
    hashed = hash_pass(password).decode()
    db.execute('insert into users(username, hashpass) values (?, ?)', (username, hashed))
    db.commit()

def query_user(username: str) -> str:
    """Get user password from db"""
    query = "select hashpass from users where username = ?"
    res = db.execute(query, (username,)).fetchone()
    return res

def home_decks(n: int) -> list:
    """Return first n decks for displaying on notes home page"""
    decks = db.execute('select deckid, name, lastedit from decks order by lastedit asc limit ?', (n,))
    decks = decks.fetchall()
    decks = [ {'deckid': x[0], 'name': x[1], 'timestamp': x[2]} for x in decks ]
    return decks

@app.route("/login")
def get_login():
    """Handler for GET requests to /login"""
    return render_template('login.html')

@app.post('/login')
def post_login():
    """Handler for POST requests to /login"""
    username = request.form['username']
    password = request.form['password']
    db_password, = query_user(username)
    if not match_pass(password, db_password.encode('UTF-8')):
        abort(401)
    session['username'] = username
    return redirect('/notes')

@app.route('/notes')
def get_notes():
    """Handler for GET requests to /notes"""
    try:
        print('user '+session['username']+'is logged in! :D')
    except KeyError:
        abort(401)
    return render_template('notes.html', decks = home_decks(10))

@app.route('/d/<deck>')
def get_deck():
    """Handler for GET requests to /d/<deck>.
    Returns HTML for entire deck contents, including cards and their contents"""
    pass

@app.route('/c/<card>')
def get_card():
    """Handler for GET requests to /c/<card>
    Return HTML for a single card including contents"""
    pass
