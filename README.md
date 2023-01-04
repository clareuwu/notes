Silly little notetaking app, complete WIP.

`app.py` flask app, routing

`models.py` models for db tables

`db.py` create table statements for db

s - static files

s/t - templates

start with `flask --app app run`

No registration page since I don't want just anyone to be able to use it, but would be easy enough to add one, just copy the login page for a basic setup.
To add a user manually, just run `create_user` in `app.py`, automatically hashes + salts pass and stores in db.

# Requirements
`sqlite3` >= 3.38.0

# TODO
- [ ] Inline search box when transcluding cards/images/files
- [ ] Add transclude for cards in other decks
- [ ] Add transclude images inside cards
- [ ] transclute other types of files inside cards
- [ ] Search bar actually do anything
- [ ] edit functionality for individual card pages
