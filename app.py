import sqlite3
from datetime import datetime
import bcrypt
from flask import Flask, render_template, request, redirect, abort, session, Response
import markdown as md
from models import User, Deck, Card, Deck_Cards
from models import db
from thefuzz import process

app = Flask(__name__, template_folder='s/t', static_folder='s')
app.config.from_pyfile('config.py')
#db = sqlite3.connect('app.db', check_same_thread=False)
db.execute('PRAGMA foreign_keys = 1')
db.commit()

def hash_pass(password: str) -> bytes:
    """Hash password w bcrypt, return hashed in bytes"""
    return bcrypt.hashpw(bytes(password, 'UTF-8'), bcrypt.gensalt())

def match_pass(password: str, hashed: bytes) -> bool:
    """Check if pw matches hashed password"""
    return bcrypt.checkpw(password.encode('UTF-8'), hashed)

def create_user(username: str, password: str) -> None:
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
    decks = db.execute('select * from decks order by lastedit desc limit ?', (n,))
    decks = decks.fetchall()
    decks = [Deck(*row) for row in decks]
    return decks

def auth() -> None:
    try: print(f"{session['username']} opened {request.path}")
    except KeyError: abort(401)

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
    else: session['username'] = username
    return redirect('/notes')

@app.route('/notes')
def get_notes():
    """Handler for GET requests to /notes"""
    auth()
    return render_template('notes.html', title = f"gm {session['username']}", decks = home_decks(100))

@app.route('/d/<deckid>')
def get_deck(deckid: int):
    """Handler for GET requests to /d/<deck>.
    Returns HTML for entire deck contents, including cards and their contents"""
    auth()
    deck = Deck.query(deckid)
    dc_rows = db.execute('select * from deck_cards where deckid = ?', (deckid,)).fetchall()
    deck_cards = [Deck_Cards(*x) for x in dc_rows]
    card_rows = [db.execute("select * from cards where cardid = ?", (x.cardid,)).fetchone() for x in deck_cards]
    cards = [Card(*x) for x in card_rows]
    return render_template('deck.html', title=deck.name, cards=cards, deck=deck, get_order=Deck_Cards.order, deckid=deckid)

@app.route('/de/<deckid>')
def get_deck_edit(deckid: int):
    """Handler for GET requests to /de/<deckid>
    Used for returning input for editing the decks name/title"""
    auth()
    deck = Deck.query(deckid)
    return render_template('title-edit.html', deck=deck)

@app.put('/de/<deckid>')
def put_deck(deckid: int):
    """Handler for PUT requests to /de/<deckid>
    Used for handling changing name of deck title"""
    auth()
    deck = Deck.query(deckid)
    title = request.form['decktitle']
    deck.name = title
    deck = deck.update()
    return render_template('deck-title.html', deck=deck)

@app.route('/ce/<cardid>')
def get_card_edit(cardid: int):
    """Handler for GET requests to /ce/<cardid>
    Used for returning input for editing a cards name when viewing single card"""
    auth()
    card = Card.query(cardid)
    return render_template('title-edit.html', deck=False, card=card)

@app.put('/ce/<cardid>')
def put_card_edit(cardid: int):
    """Handler for PUT requests to /ce/<cardid>
    Used for handling changing title of a card when viewing single card"""
    auth()
    card = Card.query(cardid)
    title = request.form['decktitle']
    card.name = title
    card = card.update()
    return render_template('deck-title.html', card=card)

@app.route('/c/<cardid>')
def get_card(cardid: int):
    """Handler for GET requests to /c/<card>
    Return HTML for a single card including contents"""
    auth()
    row = db.execute('select * from cards where cardid = ?', (cardid,)).fetchone()
    card = Card(*row)
    return render_template('deck.html', title=card.name, card=card, cards=[card])

@app.post('/new-card')
def new_card():
    """Handler for POST requests to /new-card.
    Used to create new card in db. Places into deck if on a /d page.
    Redirects to new /c page otherwise."""
    auth()
    ref = request.referrer
    if 'd' in ref.split('/'):
        card = Card.new(session['username'])
        deckid = ref.split('/')[-1]
        Deck_Cards.new(card.cardid, deckid)
        deck = Deck.query(deckid)
        deck.update()
        return render_template('card-s.html', card=card, get_order=Deck_Cards.order, deckid=deckid, deck=deck)
    else:
        card = Card.new(session['username'])
        res = Response(headers={'HX-Redirect':f"/c/{card.cardid}"})
        return res

@app.post('/new-deck')
def new_deck():
    """Handler for POST requests to /new-deck
    Returns redirect to new /d/<deckid> page."""
    auth()
    deck = Deck.new(session['username'])
    return Response(headers={'HX-Redirect':f"/d/{deck.deckid}"})

@app.get('/cse/<cardid>')
def get_cse(cardid: int):
    """Handler to render an card's edit template"""
    auth()
    card = Card.query(cardid)
    ref = request.referrer.split('/')
    deckid = False
    if 'd' in ref:
        deckid = ref[-1]
        deckid = ''.join(c for c  in deckid if c.isdigit()) # because i can not think of a less moronic way to get the deckid somehow if theres params in the url
    print('card content = '+card.content)
    return render_template('card-s-edit.html', card=card, deckid=deckid, get_order=Deck_Cards.order)

@app.put('/cse/<cardid>')
def put_cse(cardid: int):
    """Handler for PUT request to /cse/cardid
    Used for updating single cards content inside a /d/ deck page"""
    auth()

    ref = request.referrer.split('/')
    deckid = None
    deck = None
    if 'd' in ref:
        deckid = ref[-1]
        deckid = ''.join(c for c  in deckid if c.isdigit()) # because i can not think of a less moronic way to get the deckid somehow if theres params in the url
        deck = Deck.query(deckid)

    card = Card.query(cardid)
    new_name = request.form['name'].strip()
    card_name = db.execute('select name from cards where name = ?', (new_name,)).fetchone()

    if card_name and card_name[0] != new_name:
        return render_template('card-s-edit.html', deck=deck, card=card, deckid=deckid, get_order=Deck_Cards.order, error='Card name already in use')

    card.name = request.form['name']
    card.content = request.form['content']

    try:
        card.update()
        if deck: deck.update() # update last edited time when editing cards inside deck
    except sqlite3.IntegrityError:
        card = Card.query(cardid)
        return render_template('card-s-edit.html', deck=deck, card=card, deckid=deckid, get_order=Deck_Cards.order, error='Card name already in use')
    except sqlite3.OperationalError:
        card = Card.query(cardid)
        # TODO: fix whatever is causing this error when trying to save a card after getting an integrity error
        return render_template('card-s-edit.html', deck=deck, card=card, deckid=deckid, get_order=Deck_Cards.order, error='Database error, try again in a few seconds')

    card = Card.query(cardid)
    return render_template('card-s.html', deck=deck, card=card, deckid=deckid, get_order=Deck_Cards.order)

@app.delete('/csd/<deckid>/<cardid>')
def del_card(deckid: int, cardid: int):
    """Removes a card from a deck"""
    auth()
    Deck_Cards.delete(cardid, deckid)
    return ''

@app.route('/card-preview/<cardid>')
def card_preview(cardid: int):
    auth()
    card = Card.query(cardid)
    return render_template('card-preview.html', card=card)

@app.post('/include/<cardid>')
def post_include(cardid: int):
    """Handler to add existing card to existing deck"""
    auth()
    ref = request.referrer
    # slightly less stupid way to get deckid from referrer?
    deckid = ''.join([s for s in ref.split('/')[-1] if s.isdigit()])

    try: # return nothing if card already in deck
        Deck_Cards.order(cardid, deckid)
        return ""
    except: # card not already in deck
        Deck_Cards.new(cardid, deckid)

    deck = Deck.query(deckid)
    card = Card.query(cardid)
    return render_template('card-s.html', card=card, deck=deck, get_order = Deck_Cards.order, deckid=deckid)

@app.post('/search')
def get_search():
    auth()
    # my brain is fried this feels ridiculous but it stays for now
    if request.form['search'] == '': return ''
    cards = db.execute('select * from cards').fetchall()
    # list of all cards
    card_objs = [Card(*row) for row in cards]
    # make dict with card name as key to get Cards in sorted order
    card_objs = {x.name: x for x in card_objs}
    # list of just card names
    card_names = [x[1] for x in cards]
    # sorted names
    fuzzy_search = process.extract(request.form['search'], card_names, limit=10)
    # sorted Card objects
    sorted_cards = [card_objs[x[0]] for x in fuzzy_search]

    return render_template('search-results.html', cards=sorted_cards)

@app.route('/')
def index():
    return render_template('index.html')
