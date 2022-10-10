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
        new_id = values[0]
        new_name = values[1]
        new_password = values[2]

    empty_session.execute('INSERT INTO users (id, user_name, password) VALUES (:id, :user_name, :password)', {'id' : new_id,'user_name': new_name, 'password': new_password})
    row = empty_session.execute('SELECT id from users where user_name = :user_name', {'user_name': new_name}).fetchone()
    
    return row[0]


def insert_users(empty_session, values):
    for value in values:
        empty_session.execute('INSERT INTO users (id, user_name, password) VALUES (:id, :user_name, :password)', {'id' : value[0],'user_name': value[1], 'password': value[2]})

    rows = list(empty_session.execute('SELECT id from users'))
    keys = tuple(row[0] for row in rows)
    return keys

def insert_track(empty_session):
    empty_session.execute(
        'INSERT INTO tracks (track_id, title, artist_id, album_id, tracks_url, track_duration) ' 
        'VALUES (4000, "Hello, how are you, I am under the water", 1, 1, "https://www.me.me", 123);' 
    )
    row = empty_session.execute('SELECT track_id from tracks').fetchone()
    return row[0]

def insert_genres(empty_session):
    empty_session.execute(
        'INSERT INTO genres (genre_id, genre) VALUES (1, "Hello"), (2, "How are you")'
    )
    rows = list(empty_session.execute('SELECT genre_id from genres'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_track_genre_associations(empty_session, track_key, genre_keys):
    stmt = 'INSERT INTO track_genres (track_id, genre_id) VALUES (:track_id, :genre_id)'
    for genre_key in genre_keys:
        empty_session.execute(stmt, {'track_id': track_key, 'genre_id': genre_key})

def insert_commented_tracks(empty_session):
    track_key = insert_track(empty_session)
    user_key = insert_user(empty_session)

    timestamp_1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    empty_session.execute('INSERT INTO reviews (review_id, review_user, track_id, review_text, timestamp, rating) VALUES (1, :user_id, :track_id, "Comment 121441124421412214 123142124421241241 124211241241", :timestamp_1, 5)', {'user_id': user_key, 'track_id': track_key, 'timestamp_1': timestamp_1})

    row = empty_session.execute('SELECT id from users').fetchone()
    return row[0]

def make_user():
    user = User(1, "Andrew", "helloXY19")
    print(user.password)
    return user

def make_track():
    track = Track(
        4000,
        "Hello, how are you, I am under the water",
    )
    return track

def make_comment(text, track, rating, ): 
    review = Review(track, text, rating)
    return review

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

def test_saving_of_users(empty_session):
    user = make_user()
    empty_session.add(user)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT id, user_name, password FROM users'))
    assert rows == [(1, "andrew", "helloXY19")]


def test_saving_of_users_with_common_user_name(empty_session):
    insert_user(empty_session, (1, "Andrew", "1234"))
    empty_session.commit()

    with pytest.raises(IntegrityError):
        user = User(1, "Andrew", "111")
        empty_session.add(user)
        empty_session.commit()

def test_loading_of_track(empty_session):
    track_key = insert_track(empty_session)
    expected_track = make_track()
    fetched_track = empty_session.query(Track).one()

    assert expected_track == fetched_track
    assert track_key == fetched_track.track_id

def test_loading_of_tagged_track(empty_session):
    track_key = insert_track(empty_session)
    genre_keys = insert_genres(empty_session)
    insert_track_genre_associations(empty_session, track_key, genre_keys)

    fetched_track = empty_session.query(Track).one()

    assert len(fetched_track.genres) == 2
    
def test_loading_of_reviewed_track(empty_session):
    insert_commented_tracks(empty_session)

    rows = empty_session.query(User).all()
    user = rows[0]

    assert len(user.reviews) == 1
    
def test_saving_of_review(empty_session):
    track_key = insert_track(empty_session)
    user_key = insert_user(empty_session, (1, "Andrew", "1234"))

    rows = empty_session.query(Track).all()
    track = rows[0]
    user = empty_session.query(User).filter(User._User__user_name == "Andrew").one()

    # Create a new Comment that is bidirectionally linked with the User and Article.
    review_text = "Some comment text Some comment text."
    review = make_comment(review_text, track, 5)
    review.user = user

    
    # Note: if the bidirectional links between the new Comment and the User and
    # Article objects hadn't been established in memory, they would exist following
    # committing the addition of the Comment to the database.
    empty_session.add(review)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT review_user, track_id FROM reviews'))

    assert rows == [(user_key, track_key)]

def test_saving_of_article(empty_session):
    track = make_track()
    empty_session.add(track)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT track_id, title from tracks'))

    assert rows == [(4000, "Hello, how are you, I am under the water")]

def test_saving_like_tracks(empty_session): 
    track_key = insert_track(empty_session)
    user_key = insert_user(empty_session, (1, "Andrew", "1234"))
    user = empty_session.query(User).filter(User._User__user_name == "Andrew").one()

    rows = empty_session.query(Track).all()
    track = rows[0]

    user.add_liked_track(track)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT * FROM liked_tracks'))

    assert len(rows) == 1

def test_saving_removal_like_tracks(empty_session): 
    track_key = insert_track(empty_session)
    user_key = insert_user(empty_session, (1, "Andrew", "1234"))
    user = empty_session.query(User).filter(User._User__user_name == "Andrew").one()

    rows = empty_session.query(Track).all()
    track = rows[0]

    user.add_liked_track(track)
    empty_session.commit()
    user.remove_liked_track(track)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT * FROM liked_tracks'))

    assert len(rows) == 0

def test_saving_playlist(empty_session): 
    user_key = insert_user(empty_session, (1, "Andrew", "1234"))
    user = empty_session.query(User).filter(User._User__user_name == "Andrew").one()

    playlist = PlayList(1, "hello")
    user.add_playlist(playlist)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT playlist_id FROM playlists'))
    plist = rows[0]

    assert 1 == plist.playlist_id

def test_saving_playlist(empty_session): 
    user_key = insert_user(empty_session, (1, "Andrew", "1234"))
    user = empty_session.query(User).filter(User._User__user_name == "Andrew").one()

    playlist = PlayList(1, "hello")
    user.add_playlist(playlist)
    empty_session.commit()
    empty_session.query(PlayList).filter(PlayList._PlayList__list_id == playlist.list_id).delete()
    empty_session.commit()
    
    rows = list(empty_session.execute('SELECT * FROM playlists'))
    

    assert len(rows) == 0

def test_saving_added_track_to_playlist(empty_session): 
    user_key = insert_user(empty_session, (1, "Andrew", "1234"))
    track_key = insert_track(empty_session)

    user = empty_session.query(User).filter(User._User__user_name == "Andrew").one()
    rows = empty_session.query(Track).all()
    track = rows[0]

    playlist = PlayList(1, "hello")
    user.add_playlist(playlist)
    assert len(user.playlist) == 1
    playlist.add_track(track)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT * FROM user_playlists'))

    assert len(rows) == 1

def test_saving_removal_track_to_playlist(empty_session): 
    user_key = insert_user(empty_session, (1, "Andrew", "1234"))
    track_key = insert_track(empty_session)

    user = empty_session.query(User).filter(User._User__user_name == "Andrew").one()
    rows = empty_session.query(Track).all()
    track = rows[0]

    playlist = PlayList(1, "hello")
    user.add_playlist(playlist)
    assert len(user.playlist) == 1
    playlist.add_track(track)
    empty_session.commit()
    playlist.remove_track(track)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT * FROM user_playlists'))

    assert len(rows) == 0