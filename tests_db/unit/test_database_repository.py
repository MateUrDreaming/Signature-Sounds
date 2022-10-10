from datetime import date
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
from music.adapters.database_repository import SqlAlchemyRepository, SessionContextManager
from music.adapters.repository import RepositoryException
from tests_db.configtest import session_factory


def test_repository_can_add_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user_id = repo.get_number_of_users()+1
    user = User(user_id, user_name='Dave', password='123456789')
    repo.add_user(user)

    user2 = repo.get_user(user_name='dave')

    assert user2 == user and user2 is user

def test_repository_can_retrieve_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user_id = repo.get_number_of_users()+1
    repo.add_user(User(user_id, user_name='fmercury', password='8734gfe2058v'))
    user = repo.get_user('fmercury')
    assert user == User(user_id, user_name='fmercury', password='8734gfe2058v')

def test_repository_does_not_retrieve_a_non_existent_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('prince')
    assert user is None

def test_repository_can_retrieve_track_count(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_tracks = repo.get_number_of_tracks()

    # Check that the query returned 2000 tracks.
    assert number_of_tracks == 2000

def test_repository_can_add_track(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_tracks = repo.get_number_of_tracks()

    new_track_id = 4200

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

def test_repository_can_add_an_artist(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    artist = Artist(4200, 'A Test Artist')
    repo.add_artist(artist)

    assert artist in repo.get_artists()

def test_repository_can_add_an_album(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    album = Album(4200, 'A Test Album')
    album.album_url = 'www.google.com'
    album.album_type = 'Test type'
    repo.add_album(album)

    assert album in repo.get_albums()

def test_repository_get_tracks_by_id(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    #Test by query
    tracks_1 = repo.get_track_ids_for_titles("a")
    assert len(tracks_1) == 1308
    #Invalid track
    tracks2 = repo.get_track_ids_for_titles("isonas")
    assert len(tracks2) == 0

    tracks3 = repo.get_track_ids_for_album("AWOL")
    assert len(tracks3) == 4

    track4 = repo.get_track_ids_for_artist("nick")
    assert len(track4) == 54
    
    track5 = repo.get_track_ids_for_genre("rock")
    assert len(track5) == 542

    #Genres have to be properly typed
    tracks6 = repo.get_track_ids_for_genre("roock")
    assert len(tracks6) == 0

def test_repository_reviews(session_factory): 
    repo = SqlAlchemyRepository(session_factory)

    track = repo.get_track(2)
    assert track.title == "Food"

    review1 = Review(track, "Test Text", 4)
    assert review1.track == track

    repo.add_review(track, review1)
    assert len(repo.get_all_reviews()) == 1
    repo.add_review(track, review1)
    assert len(repo.get_all_reviews()) == 1
    repo.add_review(track, "Fake review")
    assert len(repo.get_all_reviews()) == 1
    assert repo.get_reviews(track) == [review1]
    #when review aint in the reviews list
    assert repo.get_reviews(repo.get_track(3)) == []

    user1 = User(7232, 'gavi', 'gavi9281')
    user1.add_review(review1)
    assert len(repo.get_user_reviews(user1)) == 1

def test_repository_likes(session_factory): 
    repo = SqlAlchemyRepository(session_factory)
    track1 = repo.get_track(2)
    track2 = repo.get_track(3)
    track3 = repo.get_track(246)

    user = User(7232, 'gavi', 'gavi9281')
    
    assert len(repo.get_all_liked_tracks(user)) == 0
    repo.add_track_to_likes(user, track1)
    assert len(repo.get_all_liked_tracks(user)) == 1
    repo.add_track_to_likes(user, track2)
    repo.add_track_to_likes(user, track3)
    assert len(repo.get_all_liked_tracks(user)) == 3

    repo.add_track_to_likes(user, track3)
    assert len(repo.get_all_liked_tracks(user)) == 3

    repo.add_track_to_likes(user, "Fake track")
    assert len(repo.get_all_liked_tracks(user)) == 3

    repo.remove_track_from_likes(user, track3)
    assert len(repo.get_all_liked_tracks(user)) == 2
    repo.remove_track_from_likes(user, "Fake track")
    assert len(repo.get_all_liked_tracks(user)) == 2


def test_repository_playlists(session_factory): 
    repo = SqlAlchemyRepository(session_factory)

    user = User(7232, 'gavi', 'gavi9281')
    user2 = User(722, 'gavii', 'gavvi9281')
    repo.add_user(user)
    repo.add_user(user2)

    play_list = PlayList(1, "Playlist1")
    assert play_list.size() == 0

    repo.add_playlist_to_lists(user, play_list)
    assert len(repo.get_all_playlist()) == 1

    play_list.add_track(repo.get_track(2))
    play_list.add_track(Track(1, 'Shivers'))

    assert repo.get_playlist_by_id(1).size() == 2
    assert repo.get_playlist_by_id(2) == None

    play_list2 = PlayList(2, "Playlist2")
    play_list2.add_track(repo.get_track(2))
    play_list2.add_track(repo.get_track(10))
    play_list2.remove_track(Track(1, 'Shivers'))
    repo.add_playlist_to_lists(user, play_list2)
    repo.add_playlist_to_lists(user2, play_list2)
    assert len(repo.get_all_playlist()) == 2
    repo.remove_playlist_from_lists(user, play_list2)
    assert len(repo.get_all_playlist()) == 1
    #All people who have saved a playlist created by another user will have their playlist DELETED :OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOoooo
    assert len(user2.playlist) == 0


    repo.remove_playlist_from_lists(user, play_list2)
    assert len(repo.get_all_playlist()) == 1
    