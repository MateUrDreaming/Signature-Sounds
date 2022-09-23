import pytest
import os
from typing import List
from music.adapters.memory_repository import MemoryRepository

from music.domainmodel.artist import Artist
from music.domainmodel.track import Track
from music.domainmodel.genre import Genre
from music.domainmodel.review import Review
from music.domainmodel.album import Album
from music.domainmodel.user import User
from music.domainmodel.playlist import PlayList
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

def test_repository_get_tracks_by_id(in_memory_repo:MemoryRepository):
    #Test by query
    tracks_1 = in_memory_repo.get_track_ids_for_titles("a")
    assert len(tracks_1) == 1308
    #Invalid track
    tracks2 = in_memory_repo.get_track_ids_for_titles("isonas")
    assert len(tracks2) == 0

    tracks3 = in_memory_repo.get_track_ids_for_album("AWOL")
    assert len(tracks3) == 4

    track4 = in_memory_repo.get_track_ids_for_artist("nick")
    assert len(track4) == 54
    
    track5 = in_memory_repo.get_track_ids_for_genre("rock")
    assert len(track5) == 542

    #Genres have to be properly typed
    tracks6 = in_memory_repo.get_track_ids_for_genre("roock")
    assert len(tracks6) == 0

def test_repository_reviews(in_memory_repo:MemoryRepository): 
    track = in_memory_repo.get_track(2)
    assert track.title == "Food"

    review1 = Review(track, "Test Text", 4)
    assert review1.track == track

    in_memory_repo.add_review(track, review1)
    assert len(in_memory_repo.get_all_reviews()) == 1
    in_memory_repo.add_review(track, review1)
    assert len(in_memory_repo.get_all_reviews()) == 1
    in_memory_repo.add_review(track, "Fake review")
    assert len(in_memory_repo.get_all_reviews()) == 1
    assert in_memory_repo.get_reviews(track) == [review1]
    #when review aint in the reviews list
    assert in_memory_repo.get_reviews(in_memory_repo.get_track(3)) == []

    user1 = User(7232, 'gavi', 'gavi9281')
    user1.add_review(review1)
    assert len(in_memory_repo.get_user_reviews(user1)) == 1
    
def test_repository_likes(in_memory_repo:MemoryRepository): 
    track1 = in_memory_repo.get_track(2)
    track2 = in_memory_repo.get_track(3)
    track3 = in_memory_repo.get_track(246)

    user = User(7232, 'gavi', 'gavi9281')
    
    assert len(in_memory_repo.get_all_liked_tracks(user)) == 0
    in_memory_repo.add_track_to_likes(user, track1)
    assert len(in_memory_repo.get_all_liked_tracks(user)) == 1
    in_memory_repo.add_track_to_likes(user, track2)
    in_memory_repo.add_track_to_likes(user, track3)
    assert len(in_memory_repo.get_all_liked_tracks(user)) == 3

    in_memory_repo.add_track_to_likes(user, track3)
    assert len(in_memory_repo.get_all_liked_tracks(user)) == 3

    in_memory_repo.add_track_to_likes(user, "Fake track")
    assert len(in_memory_repo.get_all_liked_tracks(user)) == 3

    in_memory_repo.remove_track_from_likes(user, track3)
    assert len(in_memory_repo.get_all_liked_tracks(user)) == 2
    in_memory_repo.remove_track_from_likes(user, "Fake track")
    assert len(in_memory_repo.get_all_liked_tracks(user)) == 2

def test_repository_playlists(in_memory_repo:MemoryRepository): 
    user = User(7232, 'gavi', 'gavi9281')
    user2 = User(722, 'gavii', 'gavvi9281')
    in_memory_repo.add_user(user)
    in_memory_repo.add_user(user2)

    play_list = PlayList(1, "Playlist1")
    assert play_list.size() == 0

    in_memory_repo.add_playlist_to_lists(user, play_list)
    assert len(in_memory_repo.get_all_playlist()) == 1
    play_list.add_track(Track(10, 'Bad Habit'))
    play_list.add_track(Track(1, 'Shivers'))

    assert in_memory_repo.get_playlist_by_id(1).size() == 2
    assert in_memory_repo.get_playlist_by_id(2) == None

    play_list2 = PlayList(2, "Playlist2")
    play_list2.add_track(Track(2, 'Heat Waves'))
    play_list2.add_track(Track(10, 'Bad Habit'))
    play_list2.remove_track(Track(1, 'Shivers'))
    in_memory_repo.add_playlist_to_lists(user, play_list2)
    in_memory_repo.add_playlist_to_lists(user2, play_list2)
    assert len(in_memory_repo.get_all_playlist()) == 2
    in_memory_repo.remove_playlist_from_lists(user, play_list2)
    assert len(in_memory_repo.get_all_playlist()) == 1
    #All people who have saved a playlist created by another user will have their playlist DELETED :OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOoooo
    assert len(user2.playlist) == 0


    in_memory_repo.remove_playlist_from_lists(user, "play_list2")
    assert len(in_memory_repo.get_all_playlist()) == 1
    