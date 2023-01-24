from dataclasses import dataclass, astuple
from datetime import datetime
from typing import Literal
import sqlite3
import markdown as md
from markdown.extensions.wikilinks import WikiLinkExtension
import re
db = sqlite3.connect('app.db', check_same_thread=False)
db.execute('PRAGMA foreign_keys = 1')

@dataclass
class User:
    userid: int
    username: str
    hashpass: str

@dataclass
class Deck:
    deckid: int
    name: str
    creator: str
    lastedit: int
    deleted: Literal[0, 1]

    @staticmethod
    def new(creator: str):
        timestamp = str(int(datetime.now().timestamp()))
        values = ("Untitled "+timestamp, creator)
        cur = db.cursor()
        cur.execute('insert into decks(name, creator) values (?,?)', values)
        db.commit()
        id = cur.lastrowid
        cur.close()
        row = db.execute('select * from decks where deckid=?', (id,)).fetchone()
        return Deck(*row)

    @staticmethod
    def query(deckid: int):
        row = db.execute('select * from decks where deckid=?', (deckid,)).fetchone()
        return Deck(*row)

    def isoformat(self):
        return datetime.fromtimestamp(self.lastedit)

    def update(self):
        values = (self.name, int(datetime.now().timestamp()), self.deleted, self.deckid)
        cur = db.cursor()
        cur.execute('update decks set name = ?, lastedit = ?, deleted = ? where deckid = ?', values)
        db.commit()
        cur.close()
        return Deck.query(self.deckid)

@dataclass
class Card:
    cardid: int
    name: str
    content: str
    creator: str
    lastedit: int = int(datetime.now().timestamp())
    deleted: Literal[0, 1] = 0
    # datatype: Literal["text", "image"] = "text"

    @staticmethod
    def new(creator: str):
        timestamp = str((datetime.now().timestamp()))
        values = ("Untitled "+timestamp, "", creator)
        cur = db.cursor()
        cur.execute('insert into cards(name, content, creator) values(?,?,?)', values)
        db.commit()
        id = cur.lastrowid
        cur.close()
        row = db.execute('select * from cards where cardid=?', (id,)).fetchone()
        return Card(*row)

    @staticmethod
    def query(cardid: int):
        row = db.execute('select * from cards where cardid=?', (cardid,)).fetchone()
        return Card(*row)

    def isoformat(self):
        return datetime.fromtimestamp(self.lastedit)

    def update(self) -> None:
        values = (self.name.strip(), self.content, int(datetime.now().timestamp()), self.deleted, self.cardid)
        cur = db.cursor()
        cur.execute('update cards set name=?, content=?, lastedit=?, deleted=? where cardid=?', values)
        db.commit()
        cur.close()
        return Card.query(self.cardid)

    def markdown(self) -> str:
        """Returns HTML from card elements self.content for displaying on page"""
        def url_builder(label: str, alias: str) -> str:
            label = label.strip()
            alias = alias.strip()
            try:
                cardid = db.execute('select cardid from cards where name = ?', (label,)).fetchone()[0]
            except: # card does not exist
                return f'<a href="#" class="wikilink">{alias if alias else label}</a>' # TODO: Make non-existent card links make a new card
            return f'<a href="/c/{cardid}" class="wikilink">{alias if alias else label}</a>'

        def regex_url_builder(matchobj):
            return url_builder(matchobj.group(1), matchobj.group(2))
        # markdown = md.markdown(self.content,
        #               extensions=[WikiLinkExtension(build_url=url_builder), 'fenced_code', 'codehilite'])
        markdown = md.markdown(self.content, extensions=['fenced_code', 'codehilite','tables'])
        print(markdown)
        print('content = '+self.content)
        wikilinks_regex = re.compile(r'\[\[([\w\-\s]*)\|?([\w\-\s]*)?\]\]')
        markdown = wikilinks_regex.sub(regex_url_builder, markdown)
        return md.markdown(markdown)

@dataclass
class Deck_Cards:
    dcid: int
    cardid: int
    deckid: int
    cardorder: int

    @staticmethod
    def new(cardid: int, deckid: int):
        maxorder = db.execute('select max(cardorder) from deck_cards where deckid=?', (deckid,)).fetchone()
        if maxorder != (None,):
            maxorder = maxorder[0] + 1
            values = (cardid, deckid, maxorder)
        else: values = (cardid, deckid, 1)

        cur = db.cursor()
        cur.execute('insert into deck_cards(cardid, deckid, cardorder) values (?,?,?)', values)
        db.commit()
        id = cur.lastrowid
        cur.close()

        row = db.execute('select * from deck_cards where dcid=?', (id,)).fetchone()
        return Deck_Cards(*row)

    @staticmethod
    def order(cardid: int, deckid: int) -> int:
        row = db.execute('select cardorder from deck_cards where(cardid, deckid) = (?,?)', (cardid, deckid))
        return row.fetchone()[0]

    @staticmethod
    def delete(cardid: int, deckid: int):
        db.execute('delete from deck_cards where (cardid, deckid) in (values (?, ?))', (cardid, deckid))
        db.commit()
