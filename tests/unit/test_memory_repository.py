import pytest
import os
from typing import List

from music.domainmodel.artist import Artist
from music.domainmodel.track import Track
from music.domainmodel.genre import Genre
from music.domainmodel.review import Review
from music.domainmodel.album import Album
from music.domainmodel.user import User
from music.adapters.csvdatareader import TrackCSVReader
from music.adapters.repository import RepositoryException
from conftest import in_memory_repo

def test_repository_can_add_a_track(in_memory_repo):
    track = Track(4200, 'A Test Track')
    in_memory_repo.add_track(track)

    assert in_memory_repo.get_track(4200) is track

def test_repository_can_retrieve_a_track(in_memory_repo):
    #Testing by track id
    track = in_memory_repo.get_track(2)

    #Check track has the expected album title
    assert track.title == "Food"

def test_repository_does_not_retrieve_non_existent_track(in_memory_repo):
    with pytest.raises(ValueError, match="no track with the id '3191'"):
        track = in_memory_repo.get_track(3191)
        assert str(ValueError.value) == "no track with the id '3191'"

def test_repository_can_retrieve_tracks_by_artist(in_memory_repo):
    tracks = in_memory_repo.get_tracks_by_artist(Artist(1,'AWOL'))

    #Check the query returned 4 tracks
    assert len(tracks) == 4

def test_repository_can_retrieve_tracks_by_album(in_memory_repo):
    tracks = in_memory_repo.get_tracks_by_album(Album(1, 'AWOL - A Way Of Life'))
    assert len(tracks) == 4

def test_repo_does_not_get_track_for_non_existent_artist(in_memory_repo):
    tracks = in_memory_repo.get_tracks_by_artist(Artist(0,'Test'))
    assert len(tracks) == 0

def test_repo_does_not_get_track_for_non_existent_album(in_memory_repo):
    tracks = in_memory_repo.get_tracks_by_album(Album(0, 'Test'))
    assert len(tracks) == 0

def test_repository_can_retrieve_track_by_genres(in_memory_repo):
    tracks = in_memory_repo.get_tracks_by_genre(Genre(21, 'Hip-Hop'))
    assert len(tracks) == 41

def test_repository_can_retrieve_tracks_by_id_list(in_memory_repo):
    tracks = in_memory_repo.get_tracks_by_id([2, 3])

    assert len(tracks) == 2
    assert tracks[0].title == "Food"

def test_repository_returns_empty_list_for_non_existent_ids(in_memory_repo):
    tracks = in_memory_repo.get_tracks_by_id([3192, 3193])
    
    assert len(tracks) == 0

def test_repository_can_add_a_genre(in_memory_repo):
    genre = Genre(4200, 'A Test Genre')
    in_memory_repo.add_genre(genre)

    assert genre in in_memory_repo.get_genres()

def test_repository_can_add_an_artist(in_memory_repo):
    artist = Artist(4200, 'A Test Artist')
    in_memory_repo.add_artist(artist)

    assert artist in in_memory_repo.get_artists()

def test_repository_can_add_an_album(in_memory_repo):
    album = Album(4200, 'A Test Album')
    in_memory_repo.add_album(album)

    assert album in in_memory_repo.get_albums()
