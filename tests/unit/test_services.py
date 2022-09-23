import pytest

from music.authentication.services import AuthenticationException
from music.tracks import services as tracks_services
from music.authentication import services as auth_services
from music.user import services as user_services
#from music.tracks.services import NonExistentArticleException


''' Testing authenitcation services. '''

def test_can_add_user(in_memory_repo):
    new_user_name = 'jz'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)

    user_as_dict = auth_services.get_user(new_user_name, in_memory_repo)
    assert user_as_dict['user_name'] == new_user_name

    # Check that password has been encrypted.
    assert user_as_dict['password'].startswith('pbkdf2:sha256:')


def test_cannot_add_user_with_existing_name(in_memory_repo):
    user_name = 'jz'
    password = 'abcd1A23'

    auth_services.add_user(user_name, password, in_memory_repo)

    with pytest.raises(auth_services.NameNotUniqueException):
        auth_services.add_user(user_name, password, in_memory_repo) # Trying to add it again, since no users.csv (other users already saved).


def test_authentication_with_valid_credentials(in_memory_repo):
    new_user_name = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)

    try:
        auth_services.authenticate_user(new_user_name, new_password, in_memory_repo)
    except AuthenticationException:
        assert False


def test_authentication_with_invalid_credentials(in_memory_repo):
    new_user_name = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)

    with pytest.raises(auth_services.AuthenticationException):
        auth_services.authenticate_user(new_user_name, '0987654321', in_memory_repo)


''' Testing tracks services. '''
def test_track_ids_queries(in_memory_repo): 
    tracks = tracks_services.get_track_ids_for_query(query="a", type="query", repo=in_memory_repo)
    assert len(tracks) == 1308
    tracks = tracks_services.get_track_ids_for_query(query="AWOL", type="artists", repo=in_memory_repo)
    assert len(tracks) == 4
    tracks = tracks_services.get_track_ids_for_query(query="rock", type="genres", repo=in_memory_repo)
    assert len(tracks) == 542
    tracks = tracks_services.get_track_ids_for_query(query="Blue Piano", type="albums", repo=in_memory_repo)
    assert len(tracks) == 15
    
    #invalid query
    tracks = tracks_services.get_track_ids_for_query(query="this song doesn't exist!!!", type="query", repo=in_memory_repo)
    assert len(tracks) == 0
    tracks = tracks_services.get_track_ids_for_query(query="poop", type="genres", repo=in_memory_repo)
    assert len(tracks) == 0

    #invalid type
    tracks = tracks_services.get_track_ids_for_query(query="a", type="quuery", repo=in_memory_repo)
    assert len(tracks) == 2000
    tracks = tracks_services.get_track_ids_for_query(query="AWOL", type="arrtists", repo=in_memory_repo)
    assert len(tracks) == 2000
    tracks = tracks_services.get_track_ids_for_query(query="rock", type="geenres", repo=in_memory_repo)
    assert len(tracks) == 2000
    tracks = tracks_services.get_track_ids_for_query(query="Blue Piano", type="aalbums", repo=in_memory_repo)
    assert len(tracks) == 2000

def test_track_queries(in_memory_repo): 
    tracks_id = tracks_services.get_track_ids_for_query(query="a", type="query", repo=in_memory_repo)
    tracks = tracks_services.get_tracks_by_id(tracks_id, in_memory_repo)
    assert len(tracks) == 1308

    tracks_id = tracks_services.get_track_ids_for_query(query="this song doesn't exist!!!", type="query", repo=in_memory_repo)
    tracks = tracks_services.get_tracks_by_id(tracks_id, in_memory_repo)
    assert len(tracks) == 0

    tracks_id = tracks_services.get_track_ids_for_query(query="Blue Piano", type="aalbums", repo=in_memory_repo)
    tracks = tracks_services.get_tracks_by_id(tracks_id, in_memory_repo)
    assert len(tracks) == 2000

def test_single_getting_tracks(in_memory_repo):
    #test getting a single track 
    track = tracks_services.get_track_by_id(2, in_memory_repo)
    assert track["title"] == "Food"

    track = tracks_services.get_track_object_by_id(2, in_memory_repo)
    assert track.title == "Food"

def test_adding_and_getting_reviews(in_memory_repo): 
    new_user_name = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)
    track = tracks_services.get_track_by_id(2, in_memory_repo)
    tracks_services.add_review(repo=in_memory_repo, track=track, review_text="test", rating=3, user="pmccartney")
    review = tracks_services.get_reviews(in_memory_repo, track=track)
    assert len(review) == 1
    assert review[0].track.title == track["title"]

    assert len(tracks_services.get_all_reviews(in_memory_repo)) == 1

def test_liking_tracks(in_memory_repo): 
    new_user_name = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)
    user = auth_services.get_user_object(new_user_name, in_memory_repo)
    assert user.user_name == 'pmccartney'

    tracks = tracks_services.get_track_ids_for_query(query="AWOL", type="artists", repo=in_memory_repo)

    for track_id in tracks: 
        track = tracks_services.get_track_object_by_id(track_id, in_memory_repo)

        tracks_services.add_track_to_likes(in_memory_repo, user, track)
    assert len(user.liked_tracks) == 4

    tracks_services.remove_track_from_likes(in_memory_repo, user,  tracks_services.get_track_object_by_id(3, in_memory_repo))
    assert len(user.liked_tracks) == 3

def test_playlists(in_memory_repo): 
    new_user_name = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)
    user = auth_services.get_user_object(new_user_name, in_memory_repo)
    assert user.user_name == 'pmccartney'

    user_services.add_playlist(in_memory_repo, "noobs", user)
    assert len(user.playlist) == 1

    tracks = tracks_services.get_track_ids_for_query(query="AWOL", type="artists", repo=in_memory_repo)
    for track_id in tracks: 
        tracks_services.add_to_playlist(in_memory_repo, track_id, user.playlist[0].list_id)
    
    assert user.playlist[0].size() == 4

    tracks_services.remove_from_playlist(in_memory_repo, 2, user.playlist[0].list_id)

    assert user.playlist[0].size() == 3


''' Testing user services. '''

def test_getting_all_liked_tracks(in_memory_repo):
    new_user_name = 'jnlennon'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)
    user = auth_services.get_user_object(new_user_name, in_memory_repo)
    assert user.user_name == 'jnlennon'

    tracks = tracks_services.get_track_ids_for_query(query="AWOL", type="artists", repo=in_memory_repo)

    for track_id in tracks: 
        track = tracks_services.get_track_object_by_id(track_id, in_memory_repo)

        tracks_services.add_track_to_likes(in_memory_repo, user, track)
    assert len(user_services.get_all_liked_tracks(user, in_memory_repo)) == 4

def test_adding_a_playlist(in_memory_repo):
    new_user_name = 'jnlennon'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)
    user = auth_services.get_user_object(new_user_name, in_memory_repo)
    assert user.user_name == 'jnlennon'

    title = 'A Test Playlist'
    user_services.add_playlist(in_memory_repo, title, user)
    assert len(user_services.get_user_playlists(in_memory_repo, user)) == 1

def test_getting_playlist_by_id(in_memory_repo):
    new_user_name = 'jnlennon'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)
    user = auth_services.get_user_object(new_user_name, in_memory_repo)
    assert user.user_name == 'jnlennon'

    title = 'A Test Playlist'
    user_services.add_playlist(in_memory_repo, title, user)

    playlist = user_services.get_playlist_by_id(in_memory_repo, 1)
    assert playlist.user == 'jnlennon'

def test_getting_user_playlists(in_memory_repo):
    new_user_name = 'jnlennon'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)
    user = auth_services.get_user_object(new_user_name, in_memory_repo)
    assert user.user_name == 'jnlennon'

    title = 'A Test Playlist'
    user_services.add_playlist(in_memory_repo, title, user)
    title2 = 'A Test Playlist 2'
    user_services.add_playlist(in_memory_repo, title2, user)

    assert len(user_services.get_user_playlists(in_memory_repo, user)) == 2

def test_getting_user_reviews(in_memory_repo):
    new_user_name = 'jnlennon'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)
    user = auth_services.get_user_object(new_user_name, in_memory_repo)
    assert user.user_name == 'jnlennon'

    assert len(user_services.get_user_reviews(user, in_memory_repo)) == 0

def test_removing_playlist(in_memory_repo):
    new_user_name = 'jnlennon'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)
    user = auth_services.get_user_object(new_user_name, in_memory_repo)
    assert user.user_name == 'jnlennon'

    title = 'A Test Playlist'
    user_services.add_playlist(in_memory_repo, title, user)

    user_services.remove_playlist(in_memory_repo, user, 1)
    assert len(user_services.get_user_playlists(in_memory_repo, user)) == 0

def test_changing_playlist_visibility(in_memory_repo):
    new_user_name = 'jnlennon'
    new_password = 'abcd1A23'
    auth_services.add_user(new_user_name, new_password, in_memory_repo)
    user = auth_services.get_user_object(new_user_name, in_memory_repo)
    
    title = 'A Test Playlist'
    user_services.add_playlist(in_memory_repo, title, user)

    user_services.change_visibility(in_memory_repo, user, 1)
    assert user.playlist[0].is_public == True

def test_getting_all_playlists(in_memory_repo):
    new_user_name = 'jnlennon'
    new_password = 'abcd1A23'
    auth_services.add_user(new_user_name, new_password, in_memory_repo)
    user = auth_services.get_user_object(new_user_name, in_memory_repo)
    
    title = 'A Test Playlist'
    user_services.add_playlist(in_memory_repo, title, user)

    user_services.change_visibility(in_memory_repo, user, 1)
    assert user.playlist[0].is_public == True
    assert len(user_services.get_all_playlists(in_memory_repo)) == 1

def test_adding_public_playlist(in_memory_repo):
    new_user_name = 'jnlennon'
    new_password = 'abcd1A23'
    auth_services.add_user(new_user_name, new_password, in_memory_repo)
    user = auth_services.get_user_object(new_user_name, in_memory_repo)
    
    title = 'A Test Playlist'
    user_services.add_playlist(in_memory_repo, title, user)
    user_services.change_visibility(in_memory_repo, user, 1)

    new_user_name = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)
    user2 = auth_services.get_user_object(new_user_name, in_memory_repo)
    assert user2.user_name == 'pmccartney'

    user_services.add_public_playlist(in_memory_repo, user2, 1)
    assert len(user_services.get_user_playlists(in_memory_repo, user2)) == 1  
