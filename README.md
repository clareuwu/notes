Silly little notetaking app, complete WIP.

Made with Flask, htmx, Alpine.js. Uses local sqlite3 db for persistence.

`app.py` flask app, routing, auth/cookie stuff

`models.py` models for db tables, methods for add/query/update etc.

`db.py` create table statements for db

s - static files

s/t - templates

No registration page since I don't want random people to be able to use it, but would be easy enough to add one, just copy the login page for a basic setup.
To add a user manually, just run `create_user` in `app.py`.

# Requirements
`sqlite3` >= 3.38.0

# Setup
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python db.py
```

# Run
start with `flask --app app run` or `flask --app app --debug run` for auto reloading on file changes

# TODO
- long term idea: some kind of publish feature to turn decks into blog posts, cards being separated sections
- [ ] Inline search box when transcluding cards/images/files
- [ ] Add transclude for cards in other decks
- [ ] Add transclude images inside cards
- [ ] transclute other types of files inside cards
- [ ] Search bar actually do anything
- [ ] edit functionality for individual card pages
- [ ] add lil script for making user
- [ ] render latex blocks with katex
- [ ] export notes to md documents
