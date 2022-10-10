import pytest

import datetime

from sqlalchemy.exc import IntegrityError
from tests_db.configtest import empty_session

from music.domainmodel.artist import Artist
from music.domainmodel.track import Track
from music.domainmodel.genre import Genre
from music.domainmodel.review import Review
from music.domainmodel.album import Album
from music.domainmodel.user import User
from music.domainmodel.playlist import PlayList
from music.adapters.csvdatareader import TrackCSVReader

def insert_user(empty_session, values=None):
    new_id = 40
    new_name = "Andrew"
    new_password = "1234"

    if values is not None:
        new_name = values[0]
        new_password = values[1]

    empty_session.execute('INSERT INTO users (id, user_name, password) VALUES (:id, :user_name, :password)', {'id' : new_id,'user_name': new_name, 'password': new_password})
    row = empty_session.execute('SELECT id from users where user_name = :user_name', {'user_name': new_name}).fetchone()
    
    return row[0]


def insert_users(empty_session, values):
    for value in values:
        empty_session.execute('INSERT INTO users (id, user_name, password) VALUES (:id, :user_name, :password)', {'id' : value[0],'user_name': value[1], 'password': value[2]})

    rows = list(empty_session.execute('SELECT id from users'))
    keys = tuple(row[0] for row in rows)
    return keys

def make_user():
    user = User(1, "Andrew", "111")
    return user

def test_loading_of_users(empty_session):
    users = list()
    users.append((1, "Andrew", "1234"))
    users.append((2, "Cindy", "1111"))
    insert_users(empty_session, users)

    expected = [
        User(1, "Andrew", "1234"),
        User(2, "Cindy", "999")
    ]
    assert empty_session.query(User).all() == expected