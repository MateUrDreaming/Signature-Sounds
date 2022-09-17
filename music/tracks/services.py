from typing import List, Iterable

from music.adapters.repository import AbstractRepository
from music.domainmodel.track import Track
from music.domainmodel.artist import Artist
from music.domainmodel.genre import Genre
from music.domainmodel.album import Album


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

    return track_ids

def get_tracks_by_id(id_list, repo: AbstractRepository): 
    tracks = repo.get_tracks_by_id(id_list)

    # Convert Articles to dictionary form.
    tracks_as_dict = tracks_to_dict(tracks)
    return tracks_as_dict

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