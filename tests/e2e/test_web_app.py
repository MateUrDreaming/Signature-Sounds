import pytest

from flask import session

def test_register(client):
    # Check that we retrieve the register page.
    response_code = client.get('/authentication/register').status_code
    assert response_code == 200

    # Check that we can register a user successfully, supplying a valid user name and password.
    response = client.post(
        '/authentication/register',
        data={'user_name': 'gmichael', 'password': 'CarelessWhisper1984'}
    )
    assert response.headers['Location'] == '/authentication/login'

@pytest.mark.parametrize(('user_name', 'password', 'message'), (
        ('', '', b'Your user name is required'),
        ('cj', '', b'Your user name is too short'),
        ('test', '', b'Your password is required'),
        ('test', 'test', b'Your password must be at least 8 characters, and contain an upper case letter, a lower case letter and a digit'),
        ('gmichael', 'CarelessWhisper1984', b'Your user name is already taken - please supply another')
))
def test_register_with_invalid_input(client, user_name, password, message):
    # Check that attempting to register with invalid combinations of user name and password generate appropriate error
    response = response = client.post(
        '/authentication/register',
        data={'user_name': 'gmichael', 'password': 'CarelessWhisper1984'}
    )

    # messages.
    response = client.post(
        '/authentication/register',
        data={'user_name': user_name, 'password': password}
    )
    assert message in response.data

def test_login(client, auth):
    # Check that we can retrieve the login page.
    status_code = client.get('/authentication/login').status_code
    assert status_code == 200

    response = client.post(
        '/authentication/register',
        data={'user_name': 'noob', 'password': 'Noob1234'}
    )
    assert response.headers['Location'] == '/authentication/login'

    # Check that a successful login generates a redirect to the homepage.
    response = auth.login()
    assert response.headers['Location'] == '/'


    # Check that a session has been created for the logged-in user.
    with client:
        client.get('/')
        assert session['user_name'] == 'noob'


def test_logout(client, auth):
    # Login a user.
    auth.login()

    with client:
        # Check that logging out clears the user's session.
        auth.logout()
        assert 'user_id' not in session

def test_index(client):
    # Check that we can retrieve the home page.
    response = client.get('/')
    assert response.status_code == 200
    assert b'Signature Sounds' in response.data

def test_search(client):
    response = client.get('/search')
    assert response.status_code == 200
    assert b'2000' in response.data

    #different types
    response = client.get('/search?type=query&query=night')
    assert b'Night' in response.data
    assert b'12' in response.data

    response = client.get('/search?type=artists&query=awol')
    assert b'AWOL' in response.data
    assert b'4' in response.data

    response = client.get('/search?type=genres&query=pop')
    assert b'Sir' in response.data
    assert b'40' in response.data

    #invalid search
    response = client.get('/search?type=genres&query=poop')
    assert b'No search results found, try again!' in response.data


def test_track_info_page(client):
    response = client.get('/track/2')
    assert response.status_code == 200
    assert b'Food' in response.data
    assert b'Review' in response.data


def test_review(client, auth): 
    response = client.post(
        '/authentication/register',
        data={'user_name': 'noob', 'password': 'Noob1234'}
    )

    # Check that a successful login generates a redirect to the homepage.
    auth.login()

    response = client.post(
        '/review/2',
        data={'review': 'noobs are very cool and very special.', 'rating': '4'}
    )
    assert response.headers['Location'] == '/review/2'
    
@pytest.mark.parametrize(('review', 'rating','messages'), (
    ('Who thinks Trump is a f***wit?', '4',(b'Your comment must not contain profanity')),
    ('Hey', '5',(b'Please only use between 20 - 2000 characters when writing your review')),
    ('hello, i am under the water, how are you?', '10',(b'select number between 1 and 5')),
))
def test_review_with_invalid_input(client, auth, review, rating, messages):
    response = client.post(
        '/authentication/register',
        data={'user_name': 'noob', 'password': 'Noob1234'}
    )
    # Login a user.
    auth.login()

    # Attempt to comment on an article.
    response = client.post(
        '/comment',
        data={'review': review, 'rating': rating}
    )

    # Check that supplying invalid comment text generates appropriate error messages.
    for message in messages:
        assert message in response.data
    
def test_track_info_page(client):
    response = client.get('/track/2')
    assert response.status_code == 200
    assert b'Food' in response.data
    assert b'Review' in response.data


def test_review_board(client, auth): 
    response = client.post(
        '/authentication/register',
        data={'user_name': 'noob', 'password': 'Noob1234'}
    )

    # Check that a successful login generates a redirect to the homepage.
    response = auth.login()

    response1 = client.post(
        '/review/2',
        data={'review': 'this represents review 1 which is valid.', 'rating': '3'}
    )
    response2 = client.post(
        '/review/2',
        data={'review': 'this represents another review 1 which is valid.', 'rating': '3'}
    )

    response = client.get('/review/2')
    assert b"this represents review 1 which is valid" in response.data
    assert b"this represents another review 1 which is valid" in response.data

    response = client.get('/review_board/')
    assert response.status_code == 200
    assert b"Food" in response.data
    assert b"noob" in response.data
    assert b"this represents review 1 which is valid" in response.data

#Test liking and removing liked tracks
def test_liking_tracks(client, auth): 
    response = client.post(
        '/authentication/register',
        data={'user_name': 'noob', 'password': 'Noob1234'}
    )

    # Check that a successful login generates a redirect to the homepage.
    response = auth.login()

    response1 = client.post('/track/liked/2')
    assert response1.status_code == 302

    response2 = client.get('/user/liked_tracks')
    assert response2.status_code == 200
    assert b"Food by AWOL" in response2.data

    response1 = client.post('/track/liked/2')
    assert response1.status_code == 302
    response2 = client.get('/user/liked_tracks')
    assert b"You currently have no liked tracks!" in response2.data

def test_invalid_page(client): 
    response = client.get('/user/liked_tracks')
    assert response.status_code == 302
    assert b"login" in response.data

    response = client.get('/public_playlists/1')
    assert response.status_code == 404
    assert b"404 Error" in response.data

def test_playlist(client, auth): 
    response = client.post(
        '/authentication/register',
        data={'user_name': 'noob', 'password': 'Noob1234'}
    )

    # Check that a successful login generates a redirect to the homepage.
    response = auth.login()

    #create a new playlist called `hello`
    response = client.post(
        '/user/playlists',
        data={'playlist': 'hello'}
    )

    #check if playlist is on the page
    assert response.status_code == 302
    response = client.get('/user/playlists')
    assert response.status_code == 200
    assert b"hello" in response.data
    

    #create a new playlist with a NAUGHTY WORD :OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
    response = client.post(
        '/user/playlists',
        data={'playlist': 'cock in the barbie'}
    )
    assert b"Your name must not contain profanity" in response.data
    
    #check if specified playlist generates appropriate view
    response = client.get('/playlists/1')
    assert b"hello" in response.data
    assert b"private" in response.data
    #Change playlist to public and then back to private
    response = client.post('/user/changevisibility/1')
    response = client.get('/playlists/1')
    assert b"hello" in response.data
    assert b"public" in response.data
    response = client.post('/user/changevisibility/1')
    response = client.get('/playlists/1')
    assert b"hello" in response.data
    assert b"private" in response.data
    #add tracks to playlist
    response = client.post(
        '/playlist/2',
        data={'playlist': '1'}
    )
    assert response.status_code == 302
    response = client.post(
        '/playlist/3',
        data={'playlist': '1'}
    )
    response = client.get('/playlists/1')
    assert b"Food" in response.data
    assert b"Electric" in response.data
    #remove from playlist
    response = client.get('/user/playlists')
    assert b"2" in response.data #2 tracks in currently
    response = client.post('/user/1/2')
    assert response.status_code == 302
    response = client.get('/user/playlists')
    assert b"1" in response.data #1 track after Food was removed D:

    #See playlist in public fourm
    response = client.post('/user/changevisibility/1')
    response = client.get('/public_playlists')
    assert response.status_code == 200
    assert b"hello" in response.data
    #add another playlist
    response = client.post(
        '/user/playlists',
        data={'playlist': 'euphoria'}
    )
    assert response.status_code == 302
    response = client.get('/user/playlists')
    assert response.status_code == 200
    assert b"hello" in response.data
    assert b"euphoria" in response.data
    #delete playlist
    response = client.post('/user/deleteplaylist/1')
    assert response.status_code == 302
    response = client.get('/user/playlists')
    assert response.status_code == 200
    assert b"hello" not in response.data #Because hello got deleted!
    assert b"euphoria" in response.data