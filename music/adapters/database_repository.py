from typing import List

from sqlalchemy import desc, asc, func
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from sqlalchemy.orm import scoped_session

import os
from pathlib import Path


from music.domainmodel.artist import Artist
from music.domainmodel.playlist import PlayList
from music.domainmodel.track import Track
from music.domainmodel.genre import Genre
from music.domainmodel.review import Review
from music.domainmodel.album import Album
from music.domainmodel.user import User

from music.adapters.repository import  AbstractRepository
from music.adapters.csvdatareader import TrackCSVReader


class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        # this method can be used e.g. to allow Flask to start a new session for each http request,
        # via the 'before_request' callback
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory)

    def close_current_session(self):
        if not self.__session is None:
            self.__session.close()

class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()

    def add_user(self, user: User):
        with self._session_cm as scm:
            scm.session.add(user)
            scm.commit()

    def get_user(self, user_name) -> User:
        user = None
        try:
            user = self._session_cm.session.query(User).filter(User._User__user_name == user_name).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass
        return user

    def get_number_of_users(self) -> int:
        number_of_users = self._session_cm.session.query(User).count()
        return number_of_users

    def add_track(self, track: Track):
        with self._session_cm as scm:
            scm.session.merge(track)
            scm.commit()
    
    def get_track(self, id: int) -> Track:
        track = None
        try:
            track = self._session_cm.session.query(Track).filter(Track._Track__track_id == id).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass
        return track
    
    def get_tracks_by_artist(self, target_artist: Artist) -> List[Track]:
        if target_artist is None:
            tracks = self._session_cm.session.query(Track).all()
            return tracks
        else:
            # Return tracks matching target_artist; return an empty list if there are no matches.
            tracks = self._session_cm.session.query(Track).filter(Track._Track__artist == target_artist).all()
            return tracks
    
    def get_number_of_tracks(self) -> int:
        number_of_tracks = self._session_cm.session.query(Track).count()
        return number_of_tracks

    def get_all_track_ids(self): 
        track_ids = self._session_cm.session.query(Track).all()
        return [track.track_id for track in track_ids]

    def get_tracks_by_id(self, id_list):
        tracks = self._session_cm.session.query(Track).filter(Track._Track__track_id.in_(id_list)).all()
        return tracks
    
    def get_track_ids_for_titles(self, key: str):
        # Get first occurrence of artist with artist_name.
        check_title = self._session_cm.session.query(Track).filter(Track._Track__title.ilike("%"+key+"%")).first()

        if check_title is not None:
            track_ids = list()
            tracks = self._session_cm.session.query(Track).all()
            for track in tracks:
                if (track.title).lower().find(key.lower()) != -1:
                    track_ids.append(track.track_id)
        else:
            # No Artist with name artist_name, so return an empty list.
            track_ids = list()
        
        return track_ids

    def get_track_ids_for_artist(self, artist_name: str):
        # Get first occurrence of artist with artist_name.
        check_artist = self._session_cm.session.query(Artist).filter(Artist._Artist__full_name.ilike("%"+artist_name+"%")).first()

        if check_artist is not None:
            track_ids = list()
            tracks = self._session_cm.session.query(Track).all()
            for track in tracks:
                if track.artist:
                    if (track.artist.full_name).lower().find(artist_name.lower()) != -1:
                        track_ids.append(track.track_id)
        else:
            # No Artist with name artist_name, so return an empty list.
            track_ids = list()
        
        return track_ids
    
    def get_track_ids_for_genre(self, genre_name: str):
        # Get first occurrence of genre with genre_name.
        try: 
            check_genre = self._session_cm.session.query(Genre).filter(func.lower(Genre._Genre__name) == func.lower(genre_name)).one()
        except NoResultFound: check_genre = None


        if check_genre is not None:
            track_ids = list()
            tracks = self._session_cm.session.query(Track).all()
            for track in tracks:
                for genre in track.genres:
                    if (genre.name).lower() == genre_name.lower():
                        track_ids.append(track.track_id)
        else:
            # No Genre with name genre_name, so return an empty list.
            track_ids = list()
        
        return track_ids
    
    def get_track_ids_for_album(self, album_name: str):
        # Get first occurrence of album with album_name.
        check_album = self._session_cm.session.query(Album).filter(Album._Album__title.ilike("%"+album_name+"%")).first()
        
        if check_album is not None:
            track_ids = list()
            tracks = self._session_cm.session.query(Track).all()
            for track in tracks:
                if track.album:
                    if (track.album.title).lower().find(album_name.lower()) != -1:
                        track_ids.append(track.track_id)
        else:
            # No Album with name album_name, so return an empty list.
            track_ids = list()
        
        return track_ids

    def get_tracks_by_genre(self, target_genre: Genre) -> List[Track]:
        if target_genre is None:
            tracks = self._session_cm.session.query(Track).all()
            return tracks
        else:
            # Return tracks matching target_genre; return an empty list if there are no matches.
            tracks = self._session_cm.session.query(Track).filter(target_genre in Track._Track__genres).all()
            return tracks
    
    def get_tracks_by_album(self, target_album: Album) -> List[Track]:
        if target_album is None:
            tracks = self._session_cm.session.query(Track).all()
            return tracks
        else:
            # Return tracks matching target_album; return an empty list if there are no matches.
            tracks = self._session_cm.session.query(Track).filter(Track._Track__album == target_album).all()
            return tracks

    def add_genre(self, genre: Genre):
        with self._session_cm as scm:
            scm.session.add(genre)
            scm.commit()
    
    def get_genres(self) -> List[Genre]:
        genres = self._session_cm.session.query(Genre).all()
        return genres
    
    def add_artist(self, artist: Artist):
        with self._session_cm as scm:
            scm.session.add(artist)
            scm.commit()
    
    def get_artists(self) -> List[Artist]:
        artists = self._session_cm.session.query(Artist).all()
        return artists
    
    def add_album(self, album: Album):
        with self._session_cm as scm:
            scm.session.add(album)
            scm.commit()
    
    def get_albums(self) -> List[Album]:
        albums = self._session_cm.session.query(Album).all()
        return albums
    
    def get_tracks(self) -> List[Track]:
        tracks = self._session_cm.session.query(Track).all()
        return tracks
    
    def add_review(self, track, review):
        if not isinstance(review, Review): return
        with self._session_cm as scm:
            scm.session.add(review)
            scm.commit()

    def get_reviews(self, track):
        # Get reviews of a particular Track.
        reviews = self._session_cm.session.query(Review).filter(Review._Review__track == track).all()
        return reviews
        
    def add_track_to_likes(self, user: User, track: Track): 
        with self._session_cm as scm:
            user.add_liked_track(track)
            scm.session.commit()
    
    def remove_track_from_likes(self, user: User, track: Track): 
        with self._session_cm as scm:
            user.remove_liked_track(track)
            scm.session.commit()

    def get_all_reviews(self): 
        reviews = self._session_cm.session.query(Review).all()
        return reviews
    
    def get_all_liked_tracks(self, user: User):
        return user.liked_tracks

    def add_playlist_to_lists(self, user: User, playlist: PlayList): 
        with self._session_cm as scm:
            user.add_playlist(playlist)
            scm.session.commit()
    
    def remove_playlist_from_lists(self, user, playlist: PlayList): 
        with self._session_cm as scm:
            user.remove_playlist(playlist)
            scm.session.query(PlayList).filter(PlayList._PlayList__list_id == playlist.list_id).delete()
            scm.session.commit()
    
    def get_user_playlists(self, user):
        playlists = self._session_cm.session.query(PlayList).filter(PlayList._PlayList__user == user).all()
        return playlists

    def get_playlist_id(self):
        count = self._session_cm.session.query(PlayList).count()
        return count + 1
    
    def get_all_playlist(self): 
        playlists = self._session_cm.session.query(PlayList).all()
        return playlists
    
    def get_playlist_by_id(self, id: int): 
        playlist = self._session_cm.session.query(PlayList).filter(PlayList._PlayList__list_id == id).first()
        return playlist
    
    def get_user_reviews(self, user): 
        # Get reviews from a particular User.
        reviews = self._session_cm.session.query(Review).filter(Review._Review__user == user).all()
        return reviews
    
    def add_track_to_playlist(self, track: Track, playlist: PlayList):
        with self._session_cm as scm:
            playlist.add_track(track)   
            scm.session.commit()
    
    def remove_track_from_playlist(self, track: Track, playlist: PlayList):
        with self._session_cm as scm:
            playlist.remove_track(track)
            scm.session.commit()

    def get_visible_playlists(self): 
        playlists = self._session_cm.session.query(PlayList).filter(PlayList._PlayList__is_public == 1).all()
        return playlists
    
    def change_vis_of_playlist(self, playlist: PlayList):
        print(playlist.is_public)
        with self._session_cm as scm:
            playlist.switch_visibility()
            scm.session.commit()
        print(playlist.is_public)
        
def populate_two(data_path: Path, repo: SqlAlchemyRepository, database_mode=False):
    """ Populates the given repository using data at the given path. """
    dirname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    albums_file_name = os.path.join(dirname, 'adapters/data/raw_albums_excerpt.csv')
    tracks_file_name = os.path.join(dirname, 'adapters/data/raw_tracks_excerpt.csv')
    reader = TrackCSVReader(albums_file_name, tracks_file_name, database_mode)
    reader.read_csv_files()

    for artist in reader.dataset_of_artists:
        repo.add_artist(artist)

    for genre in reader.dataset_of_genres:
        repo.add_genre(genre)
    
    for album in reader.dataset_of_albums:
        repo.add_album(album)
    
    for track in reader.dataset_of_tracks:
        repo.add_track(track)