Little notes app I'm making since I'm not happy with any other note taking/knowledge base apps, WIP. Inspired by Obsidian.md mostly. 

Made with Flask, htmx, Alpine.js. Uses local sqlite3 db for persistence.

Example preview:

<p align="center">
<img width="80%" align="center" alt="image" src="https://user-images.githubusercontent.com/87212918/217326853-e517f336-9eec-4da7-b57d-606cb6101c81.png">
</p>

---

`app.py` flask app, routing, auth/cookie stuff

`models.py` models for db tables, methods for add/query/update etc.

`db.py` create table statements for db

s - static files

s/t - templates

# Requirements
`sqlite3` >= 3.38.0

`python3` >= 3.8

# Setup
To install requirements and initialize db:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python db.py
```

Then add yourself a user: `python add_user.py <username> <password>`, replacing `<username>` and `<password>` with your own desired account info.

> Note, there's currently no authentication for displaying cards only to the account that made them, so if you have more than one user they can all see/edit every card in the db. I'm mostly making this for my own personal use, but I'm planning on implementing that eventually.

To generate secret key:
```
python3
>>> import os
>>> os.urandom(16)
```
Put generated bytes in config.py: `SECRET_KEY = 'bytes here'`

# Run
start with `flask --app app run` or `flask --app app --debug run` for auto reloading on file changes. Otherwise run behind nginx long-term.

# Keyboard shortcuts
outside text inputs:
- `shift-d`: new deck
- `shift-c`: new card
- `shift-s`: search bar for including cards into decks
- `shift-e`: with a card clicked, opens edit card

inside card textarea:
- `escape`, `cmd-enter`, `shift-enter`: save content


# To do
- maybe: some kind of publish feature to turn decks into blog posts, cards being separated sections
- [ ] Inline search box when transcluding cards/images/files
- [ ] way to reorder cards in deck
- [x] Add transclude for cards in other cards
- [x] Add include existing card in current deck
- [ ] Add transclude images inside cards
- [ ] transclude other types of files inside cards
- [x] edit functionality for individual card pages
- [ ] middleware for auth to redirect instead of 401
- [x] add lil script for making user
- [x] render latex blocks with katex
- [ ] export notes to md documents
- [ ] Kanban style deck/page for organizing projects?
