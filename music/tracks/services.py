from os import abort
from typing import List, Iterable

from music.adapters.repository import AbstractRepository
from music.domainmodel.review import Review
from music.domainmodel.track import Track
from music.domainmodel.artist import Artist
from music.domainmodel.genre import Genre
from music.domainmodel.album import Album
from music.domainmodel.user import User



def get_track_ids_for_query(query, type, repo: AbstractRepository):
    if not query: 
        track_ids = list(repo.get_all_track_ids())
    else: 
        if type == "query": 
            track_ids = repo.get_track_ids_for_titles(query)
        elif type == "artists": 
            track_ids = repo.get_track_ids_for_artist(query)
        elif type == "genres": 
            track_ids = repo.get_track_ids_for_genre(query)
        elif type == "albums": 
            track_ids = repo.get_track_ids_for_album(query)
        else: track_ids = list(repo.get_all_track_ids())

    return track_ids

def get_tracks_by_id(id_list, repo: AbstractRepository): 
    tracks = repo.get_tracks_by_id(id_list)

    # Convert Articles to dictionary form.
    tracks_as_dict = tracks_to_dict(tracks)
    return tracks_as_dict

def get_track_by_id(track_id, repo: AbstractRepository): 
    track = repo.get_track(track_id)

    # Convert Articles to dictionary form.
    track_as_dict = track_to_dict(track)
    return track_as_dict

def get_track_object_by_id(track_id, repo: AbstractRepository): 
    return repo.get_track(track_id)

def get_reviews(repo: AbstractRepository, track): 
    if track is None:
        raise NonExistentArticleException
    track = repo.get_track(track["id"])
    reviews = repo.get_reviews(track)
    return reviews

def add_review(repo: AbstractRepository, track, review_text, rating, user): 

    if track is None:
        raise NonExistentArticleException
    track = repo.get_track(track["id"])
    # Create review.
    review = Review(track, review_text, rating)
    review.user = user
    # Update the repository.
    repo.add_review(track, review)
    user = repo.get_user(user)
    user.add_review(review)

def get_all_reviews(repo: AbstractRepository): 
    return repo.get_all_reviews()

def add_track_to_likes(repo: AbstractRepository, user: User, track: Track) -> None:
    """ Adds the given movie to the given user's watchlist. """
    repo.add_track_to_likes(user, track)


def remove_track_from_likes(repo: AbstractRepository, user: User, track: Track) -> None:
    """ Removes the given movie from the given user's watchlist. """
    repo.remove_track_from_likes(user, track)

def add_playlist(repo:AbstractRepository, track_id, playlist_id): 
    track = repo.get_track(int(track_id))
    playlist = repo.get_playlist_by_id(int(playlist_id))
    playlist.add_track(track)

def remove_playlist(repo:AbstractRepository, track_id, playlist_id): 
    track = repo.get_track(int(track_id))
    playlist = repo.get_playlist_by_id(int(playlist_id))
    playlist.remove_track(track)



'''
===========
CONVERT TO DICT
'''

def track_to_dict(track: Track):
    track_dict = {
        'id': track.track_id,
        'title': track.title,
        'artist': track.artist.full_name,
        'album': track.album,
        'url': track.track_url,
        'duration': track.track_duration,
        'genres': track.genres
    }

    return track_dict

def tracks_to_dict(tracks: Iterable[Track]):
    return [track_to_dict(track) for track in tracks]

def review_to_dict(review: Review):
    comment_dict = {
        'user_name': review.user.user_name,
        'article_id': review.article.id,
        'comment_text': review.comment,
        'timestamp': review.timestamp
    }
    return comment_dict
class NonExistentArticleException(Exception):
    pass

