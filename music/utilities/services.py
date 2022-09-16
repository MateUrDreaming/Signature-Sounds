from typing import Iterable
import random

from music.adapters.repository import AbstractRepository
from music.domainmodel import track


def get_track_names(repo: AbstractRepository):
    tracks = repo.get_tracks()
    track_names = [track.title for track in tracks]

    return track_names






