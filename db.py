import sqlite3
con = sqlite3.connect('app.db')

def make_table_wrapper(query: str, table: str = None, drop: bool = False):
    """Wrapper to not repeat drop table logic"""
    con.execute('PRAGMA foreign_keys = ON;')
    if drop: con.execute(f'drop table if exists {table};')
    con.execute(query)
    con.commit()

def create_users_table(drop = False):
    """Create table containing user info"""
    con.execute('PRAGMA foreign_keys = ON;')
    make_table_wrapper('''create table users(
        userid integer primary key,
        username text unique not null,
        hashpass text not null
        );''', 'users', drop)

def create_decks_table(drop = False):
    """Create sqlite table containing deck info"""
    make_table_wrapper('''create table decks(
        deckid integer primary key,
        name text unique not null,
        creator text not null,
        lastedit integer default (unixepoch()) not null,
        deleted integer default 0 not null,
        foreign key (creator) references users(username)
        );''', 'decks', drop)

def create_cards_table(drop = False):
    """Create table for card info"""
    make_table_wrapper('''create table cards(
        cardid integer primary key autoincrement,
        name text unique not null,
        content text not null,
        creator text not null,
        lastedit integer default (unixepoch()) not null,
        deleted integer default 0 not null,
        datatype text default "text" not null,
        foreign key (creator) references users(username)
        );''', 'cards', drop)

def create_deck_entries_table(drop = False):
    """Create table to contain references for which cards are in which deck,
    allows one card to be in multiple decks"""
    make_table_wrapper('''create table deck_cards(
        dcid integer primary key,
        cardid integer not null,
        deckid integer not null,
        cardorder integer not null,
        foreign key (deckid) references decks(deckid) on delete cascade,
        foreign key (cardid) references cards(cardid) on delete cascade
        );''', 'deck_cards', drop)

create_decks_table(True)
create_cards_table(True)
create_deck_entries_table(True)
