from random import randint
from werkzeug.security import generate_password_hash, check_password_hash

from music.adapters.repository import AbstractRepository
from music.domainmodel.user import User

class NameNotUniqueException(Exception):
    pass


class UnknownUserException(Exception):
    pass


class AuthenticationException(Exception):
    pass

def add_user(user_name: str, password: str, repo: AbstractRepository):
    #Check the given user name is available
    user = repo.get_user(user_name)
    if user is not None:
        raise NameNotUniqueException
    
    #Encrypt password so that the database doesn't store passwords 'in the clear'
    password_hash = generate_password_hash(password)

    #Create and store the new User, with password encrypted. Also given a user_id in linear fashion.
    if repo.get_number_of_users() == 0:
        user_id = 1
    elif repo.get_number_of_users() > 0:
        user_id = repo.get_number_of_users() + 1

    new_user = User(user_id, user_name, password_hash)   
    repo.add_user(new_user)

def get_user(user_name: str, repo: AbstractRepository):
    user = repo.get_user(user_name)
    if user is None:
        raise UnknownUserException

    return user_to_dict(user)

def authenticate_user(user_name: str, password: str, repo: AbstractRepository):
    authenticated = False

    user = repo.get_user(user_name)
    if user is not None:
        authenticated = check_password_hash(user.password, password)
    if not authenticated:
        raise AuthenticationException

# ===================================================
# Functions to convert model entities to dictionaries
# ===================================================

def user_to_dict(user: User):
    user_dict = {
        'user_name': user.user_name,
        'password': user.password
    }
    return user_dict