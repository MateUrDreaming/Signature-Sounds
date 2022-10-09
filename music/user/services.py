from music.adapters.repository import AbstractRepository
from music.domainmodel.playlist import PlayList
from music.domainmodel.review import Review
from music.domainmodel.track import Track
from music.domainmodel.artist import Artist
from music.domainmodel.genre import Genre
from music.domainmodel.album import Album
from music.domainmodel.user import User

def get_all_liked_tracks(user, repo: AbstractRepository): 
    return repo.get_all_liked_tracks(user)

def add_playlist(repo: AbstractRepository, title: str, user: User): 
    id = repo.get_playlist_id()
    play_list = PlayList(id, title)
    play_list.user = user
    repo.add_playlist_to_lists(user, play_list)
    

def get_playlist_by_id(repo: AbstractRepository, id: int): 
    return repo.get_playlist_by_id(id)

def get_user_playlists(repo: AbstractRepository, user: User): 
    return repo.get_user_playlists(user)

def get_user_reviews(user, repo): 
    return repo.get_user_reviews(user)

def remove_playlist(repo:AbstractRepository, user: User, playlist_id): 
    play_list = repo.get_playlist_by_id(playlist_id)
    repo.remove_playlist_from_lists(user, play_list)

def change_visibility(repo, user, playlist_id): 
    playlist = repo.get_playlist_by_id(int(playlist_id))
    playlist.switch_visibility()

def get_all_playlists(repo: AbstractRepository): 
    return repo.get_visible_playlists()

def add_public_playlist(repo: AbstractRepository,user: User, playlist_id): 
    playlist = repo.get_playlist_by_id(int(playlist_id))
    user.add_playlist(playlist)