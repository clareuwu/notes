from dataclasses import dataclass, astuple
from datetime import datetime
from typing import Literal
import sqlite3
import markdown as md
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
    lastedit: int = int(datetime.now().timestamp())
    deleted: Literal[0, 1] = 0

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
        db.execute('update decks set name = ?, lastedit = ?, deleted = ? where deckid = ?', values)
        db.commit()

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
        values = (self.name, self.content, int(datetime.now().timestamp()), self.deleted, self.cardid)
        db.execute('update cards set name=?, content=?, lastedit=?, deleted=? where cardid=?', values)
        db.commit()

    def markdown(self) -> str:
        return md.markdown(self.content)

@dataclass
class Deck_Cards:
    dcid: int
    cardid: int
    deckid: int
    cardorder: int

    @staticmethod
    def new(cardid: int, deckid: int, cardorder: int):
        values = (cardid, deckid, cardorder)
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
