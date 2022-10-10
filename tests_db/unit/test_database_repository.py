from curses.ascii import US
from datetime import date
from re import U
from typing import List
import pytest
import os

from music.domainmodel.artist import Artist
from music.domainmodel.track import Track
from music.domainmodel.genre import Genre
from music.domainmodel.review import Review
from music.domainmodel.album import Album
from music.domainmodel.user import User
from music.domainmodel.playlist import PlayList
from music.adapters.csvdatareader import TrackCSVReader

import music.adapters.repository as repo
from music.adapters.database_repository import SqlAlchemyRepository
from music.adapters.repository import RepositoryException

def test_repository_can_add_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = User('Dave', '123456789')
    repo.add_user(user)

    repo.add_user(User('Martin', '123456789'))

    user2 = repo.get_user('Dave')

    assert user2 == user and user2 is user

def test_repository_can_retrieve_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    repo.add_user(User('fmercury', '8734gfe2058v'))
    user = repo.get_user('fmercury')
    assert user == User('fmercury', '8734gfe2058v')

def test_repository_does_not_retrieve_a_non_existent_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('prince')
    assert user is None

def test_repository_can_retrieve_track_count(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_tracks = repo.get_number_of_tracks()

    # Check that the query returned 2082 tracks.
    assert number_of_tracks == 2082

def test_repository_can_add_track(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_tracks = repo.get_number_of_tracks()

    new_track_id = number_of_tracks + 1

    track = Track(4200, 'A Test Track')
    repo.add_track(track)

    assert repo.get_track(new_track_id) == track

def test_repository_can_retrieve_track(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    track = repo.get_track(2)

    # Check that the Track has the expected title.
    assert track.title == "Food"

def test_repository_does_not_retrieve_a_non_existent_track(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    track = repo.get_track(4200)
    assert track is None

def test_repository_can_retrieve_tracks_by_artist(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    tracks = repo.get_tracks_by_artist(Artist(1,'AWOL'))

    #Check the query returned 4 tracks
    assert len(tracks) == 4

def test_repository_can_retrieve_tracks_by_album(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    tracks = repo.get_tracks_by_album(Album(1, 'AWOL - A Way Of Life'))
    assert len(tracks) == 4

def test_repo_does_not_get_track_for_non_existent_artist(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    tracks = repo.get_tracks_by_artist(Artist(0,'Test'))
    assert len(tracks) == 0

def test_repo_does_not_get_track_for_non_existent_album(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    tracks = repo.get_tracks_by_album(Album(0, 'Test'))
    assert len(tracks) == 0

def test_repository_can_retrieve_track_by_genres(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    tracks = repo.get_tracks_by_genre(Genre(21, 'Hip-Hop'))
    assert len(tracks) == 41

def test_repository_can_retrieve_tracks_by_id_list(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    tracks = repo.get_tracks_by_id([2, 3])

    assert len(tracks) == 2
    assert tracks[0].title == "Food"

def test_repository_returns_empty_list_for_non_existent_ids(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    tracks = repo.get_tracks_by_id([3192, 3193])
    
    assert len(tracks) == 0

def test_repository_can_add_a_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    genre = Genre(4200, 'A Test Genre')
    repo.add_genre(genre)

    assert genre in repo.get_genres()

