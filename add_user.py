import sqlite3
import sys
from app import create_user

"""Usage: python create_user username password"""
db = sqlite3.connect('app.db')
create_user(sys.argv[1], sys.argv[2])
