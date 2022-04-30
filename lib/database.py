import json
import logging
import sqlite3

from .structures import Menu
from . import config

tables = [
    """
    CREATE TABLE `Users`(
        PhoneNumber NUMBER,
        Name TEXT,
        Permissions JSON,
        PRIMARY KEY(PhoneNumber)
    )
    """,
    """
    CREATE TABLE `MenuState`(
        User NUMBER,
        Menu MENU,
        PRIMARY KEY(User),
        FOREIGN KEY(User)
            REFERENCES Users(PhoneNumber)
            ON DELETE CASCADE
    )
    """
]

sqlite3.register_adapter(dict, json.dumps)
sqlite3.register_adapter(list, json.dumps)
sqlite3.register_adapter(Menu, Menu.dump)

sqlite3.register_converter('JSON', json.loads)
sqlite3.register_converter('MENU', Menu.fromString)


class Database(object):
    def __enter__(self, name='default'):
        self.connection = sqlite3.connect(config.get_database()['address'], detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = self.connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        return cursor
    
    def __exit__(self, *args):
        self.connection.commit()
        self.connection.close()


def setup_tables():
    logging.info("Setting up tables.")
    with Database() as db:
        for sql in tables:
            db.execute(sql)

def update_user_permissions(phonenumber, permissions):
    with Database() as db:
        db.execute("UPDATE Users SET Permissions=? WHERE PhoneNumber=?", (permissions, phonenumber))


def update_user(phonenumber, name, permissions, menu):
    with Database() as db:
        db.execute("UPDATE Users SET Name = ?, Permissions = ? WHERE PhoneNumber = ?", (name, permissions, phonenumber))
        db.execute("INSERT OR REPLACE INTO MenuState(Menu, User) VALUES (?, ?)", (menu, phonenumber))


def update_user_name(phonenumber, name):
    with Database() as db:
        db.execute("UPDATE Users SET Name=? WHERE PhoneNumber=?", (name, phonenumber))

def create_user(phonenumber, name=None, permissions=None):
    if not permissions:
        permissions = {}
    with Database() as db:
        db.execute("INSERT INTO Users(PhoneNumber, Name, Permissions) VALUES (?, ?, ?)", (phonenumber, name, permissions))

def get_user(phonenumber=None):
    with Database() as db:
        cursor = db.execute("""
            SELECT 
                u.*,
                m.Menu
            FROM Users AS u
            LEFT OUTER JOIN MenuState AS m
                ON m.User = u.PhoneNumber
            WHERE PhoneNumber = ?
            LIMIT 1        
        """, (phonenumber,))
        item = cursor.fetchone()
    return item

def delete_user(phonenumber=None):
    with Database() as db:
        cursor = db.execute("SELECT * FROM Users WHERE PhoneNumber = ? LIMIT 1", (phonenumber,))
        item = cursor.fetchone()
    return item

def set_menu_state(phonenumber, menu):
    with Database() as db:
        db.execute("INSERT OR REPLACE INTO MenuState(User, Menu) VALUES (?, ?)", (phonenumber, menu))

