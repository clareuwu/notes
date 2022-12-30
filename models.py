from dataclasses import dataclass
from datetime import datetime

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
    lastedit: int # in unix epoch time
    deleted: 0 | 1

@dataclass
class Card:
    cardid: int
    name: str
    content: str
    creator: str
    lastedit: int # in unix epoch time
    deleted: 0 | 1
    datatype: "Text" | "Image"

@dataclass
class Deck_Cards:
    dcid: int
    cardid: int
    deckid: int
