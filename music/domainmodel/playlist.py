import imp
from xmlrpc.client import boolean
from music.domainmodel.track import Track


class PlayList:

    def __init__(self, list_id, title: str):
        if type(list_id) is not int or list_id < 0:
            raise ValueError("User ID should be a non negative integer.")
        self.__list_id = list_id

        if type(title) is str and title.strip() != '':
            self.__title: str = title.strip()
        else:
            self.__title = None

        self.__list_of_tracks = []
        self.__user = None
        self.__is_public = False

    @property
    def list_id(self) -> int:
        return self.__list_id
    
    @property
    def title(self) -> str:
        return self.__title

    @title.setter
    def title(self, new_title):
        if type(new_title) is str and new_title.strip() != '':
            self.__title = new_title.strip()
        else:
            self.__title = None
    
    @property
    def user(self) -> str:
        return self.__user

    @user.setter
    def user(self, user):
        from music.domainmodel.user import User
        if isinstance(user, User):
            self.__user = user
        else:
            self.__user = None
            raise ValueError("invalid user")
    
    @property
    def is_public(self) -> boolean:
        return self.__is_public

    @property
    def tracks(self):
        return self.__list_of_tracks   

    def size(self):
        size_playlist = len(self.__list_of_tracks)
        if size_playlist > 0:
            return size_playlist
        else: return 0

    def add_track(self, track: Track):
        if track not in self.__list_of_tracks:
            self.__list_of_tracks.append(track)
        else:
            pass

    def first_track_in_list(self):
        if len(self.__list_of_tracks) > 0:
            return self.__list_of_tracks[0]
        else:
            return None

    def remove_track(self, track):
        if track in self.__list_of_tracks:
            self.__list_of_tracks.remove(track)
        else:
            pass

    def select_track_to_listen(self, index):
        if 0 <= index < len(self.__list_of_tracks):
            return self.__list_of_tracks[index]
        else:
            return None
    
    def switch_visibility(self): 
        if self.__is_public: 
            self.__is_public = False
        else: 
            self.__is_public = True

    def __iter__(self):
        self.__current = 0
        return self

    def __next__(self):
        if self.__current >= len(self.__list_of_tracks):
            raise StopIteration
        else:
            self.__current += 1
            return self.__list_of_tracks[self.__current - 1]

    def __repr__(self):
        return f'<Playlist {self.title}, Playlist id = {self.list_id}>'
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.list_id == other.list_id

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return True
        return self.list_id < other.list_id

    def __hash__(self):
        return hash(self.list_id)