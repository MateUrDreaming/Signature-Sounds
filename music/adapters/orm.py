from datetime import datetime
from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, DateTime,
    ForeignKey, func
)
from sqlalchemy.orm import mapper, relationship, synonym

from music.domainmodel.artist import Artist
from music.domainmodel.playlist import PlayList
from music.domainmodel.track import Track
from music.domainmodel.genre import Genre
from music.domainmodel.review import Review
from music.domainmodel.album import Album
from music.domainmodel.user import User

# global variable giving access to the MetaData (schema) information of the database
metadata = MetaData()

users_table = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_name', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False)
)

artist_table = Table(
    'artists', metadata,
    Column('artist_id', Integer, primary_key=True, autoincrement=True),
    Column('full_name', String(255), unique=True, nullable=False)
)

album_table = Table(
    'albums', metadata,
    Column('album_id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), nullable=False),
    Column('album_url', String(255), unique=True, nullable=False),
    Column('album_type', String(255), unique=True, nullable=False),
    Column('release_year', Integer)
    
)

tracks_table = Table(
    'tracks', metadata,
    Column('track_id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), nullable=False),
    Column('artist_id', ForeignKey('artists.artist_id')),
    Column('album_id', ForeignKey('albums.album_id')),
    Column('tracks_url', String(255)),
    Column('track_duration', Integer)
)

genre_table = Table(
    'genres', metadata,
    Column('genre_id', Integer, primary_key=True, autoincrement=True),
    Column('genre', String(255), unique=True, nullable=False)
)

track_genre_table = Table(
    'track_genres', metadata,
    Column('track_id', Integer, ForeignKey('tracks.track_id'), unique=True),
    Column('genre_id', Integer, ForeignKey('genres.genre_id'), unique=True)
)

reviews_table = Table(
    'reviews', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user', ForeignKey('users.user_name')),
    Column('track_id', ForeignKey('tracks.track_id')),
    Column('review_text', String(1024), nullable=False),
    Column('timestamp', DateTime, nullable=False, server_default=func.now()),
    Column('rating', Integer)
)


def map_model_to_tables():
    mapper(User, users_table, properties={
        '_User__user_name': users_table.c.user_name,
        '_User__password': users_table.c.password,
        '_User__reviews': relationship(Review, backref='_review__user')
    })

    mapper(Artist, artist_table, properties={
        '_Artist__id': artist_table.c.artist_id,
        '_Artist__date': artist_table.c.full_name
    })

    mapper(Album, album_table, properties={
        '_Album__album_id': album_table.c.album_id,
        '_Album__title': album_table.c.title,
        '_Album__album_url': album_table.c.album_url,
        '_Album__album_type': album_table.c.album_type,
        '_Album__release_year': album_table.c.release_year
    })

    mapper(Track, tracks_table, properties={
        '_Track__track_id': tracks_table.c.track_id,
        '_Track__title': tracks_table.c.title,
        '_Track__artist': relationship(Artist),
        '_Track__album': relationship(Album),
        '_Track__track_duration': tracks_table.c.track_duration,
        '_Track__genres': relationship(Genre, secondary=track_genre_table)
    })

    mapper(Genre, genre_table, properties={
        '_Genre__genre_id': genre_table.c.genre_id,
        '_Genre__name': genre_table.c.genre
    })

    
    mapper(Review, reviews_table, properties={
        '_Review__user': relationship(User),
        '_Review__track': relationship(Track),
        '_Review__review_text': reviews_table.c.review_text,
        '_Review__timestamp': reviews_table.c.rating,
        '_Review__rating': reviews_table.c.rating
    })

