import profile
from flask import Blueprint, abort
from flask import request, render_template, redirect, url_for, session, abort

from better_profanity import profanity
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

import music.adapters.repository as repo
import music.user.services as services
from music.authentication.authentication import login_required
import music.authentication.services as auth
from music.utilities.utilities import PlaylistForm

user_blueprint = Blueprint('user_bp', __name__)

    
@user_blueprint.route('/user/liked_tracks', methods=['GET'])
@login_required
def profile():
    user=None
    first_track_url = None
    last_track_url = None
    next_track_url = None
    prev_track_url = None
    tracks_per_page = 5
    try:
        user = auth.get_user_object(session['user_name'], repo.repo_instance)
    except ValueError:
        # No user with the given username
        pass
    except KeyError:
        # No active session, anonymous/guest user
        abort(404)
        pass
    except auth.UnknownUserException:
        # Invalid session
        session.clear()
        abort(404)
        

    tracks = services.get_all_liked_tracks(user, repo.repo_instance)
    cursor = request.args.get('cursor')

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)
    
    tracks_to_be_displayed = tracks[cursor:cursor + tracks_per_page]

    cursor = (cursor // tracks_per_page) * tracks_per_page
    
    if cursor > 0:
        # There are preceding articles, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_track_url = url_for('user_bp.profile', cursor=cursor - tracks_per_page)
        first_track_url = url_for('user_bp.profile')

    

    if cursor + tracks_per_page < len(tracks):
        # There are further articles, so generate URLs for the 'next' and 'last' navigation buttons.
        next_track_url = url_for('user_bp.profile', cursor=cursor + tracks_per_page)
    
        last_cursor = tracks_per_page * int(len(tracks) / tracks_per_page)
        if len(tracks) % tracks_per_page == 0:
            last_cursor -= tracks_per_page
        last_track_url = url_for('user_bp.profile', cursor=last_cursor)
    
    return render_template("profile.html", 
    user=user, 
    liked_tracks = tracks_to_be_displayed, 
    prev_track_url = prev_track_url,
    first_track_url = first_track_url,
    next_track_url = next_track_url,
    last_track_url = last_track_url,
    )

@user_blueprint.route('/user/playlists', methods=['GET', 'POST'])
@login_required
def playlists():
    user=None
    sesh = False
    try:
        user = auth.get_user_object(session['user_name'], repo.repo_instance)
        sesh = True
    except ValueError:
        # No user with the given username
        pass
    except KeyError:
        # No active session, anonymous/guest user
        abort(404)
        pass
    except auth.UnknownUserException:
        # Invalid session
        session.clear()
        abort(404)
    
    playlists = services.get_user_playlists(repo.repo_instance, user)

    form = PlaylistForm()
    if form.validate_on_submit() and sesh:
        # Use the service layer to store the new review.
        services.add_playlist(repo.repo_instance, form.playlist.data, user)
        # Reload the page to show the new review
        return redirect(url_for('user_bp.playlists'))
    
    return render_template ('playlists.html', 
    user=user,
    playlists = playlists,
    form=form, 
    leng = len(playlists)
    )

@user_blueprint.route('/user/playlists/<int:playlist_id>', methods=['GET'])
@login_required
def playlistID(playlist_id: int):
    try:
        user = auth.get_user_object(session['user_name'], repo.repo_instance)
    except ValueError:
        # No user with the given username
        pass
    except KeyError:
        # No active session, anonymous/guest user
        pass
    except auth.UnknownUserException:
        # Invalid session
        session.clear()
        pass
    playlist = services.get_playlist_by_id(repo.repo_instance, playlist_id)

    if playlist: 
        leng = playlist.size()
    else: leng = 0

    return render_template ('playlistid.html', 
    leng = leng,
    playlist = playlist
    )


@user_blueprint.route('/user/reviews', methods=['GET'])
@login_required
def review():
    user=None
    first_review_url = None
    last_review_url = None
    next_review_url = None
    prev_review_url = None
    reviews_per_page = 3
    try:
        user = auth.get_user_object(session['user_name'], repo.repo_instance)
    except ValueError:
        # No user with the given username
        pass
    except KeyError:
        # No active session, anonymous/guest user
        abort(404)
        pass
    except auth.UnknownUserException:
        # Invalid session
        session.clear()
        abort(404)
        

    reviews = services.get_user_reviews(user, repo.repo_instance)
    cursor = request.args.get('cursor')

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)
    
    reviews_to_be_displayed = reviews[cursor:cursor + reviews_per_page]

    cursor = (cursor // reviews_per_page) * reviews_per_page
    
    if cursor > 0:
        # There are preceding articles, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_review_url = url_for('user_bp.profile', cursor=cursor - reviews_per_page)
        first_review_url = url_for('user_bp.profile')

    

    if cursor + reviews_per_page < len(reviews):
        # There are further articles, so generate URLs for the 'next' and 'last' navigation buttons.
        next_review_url = url_for('user_bp.profile', cursor=cursor + reviews_per_page)
    
        last_cursor = reviews_per_page * int(len(reviews) / reviews_per_page)
        if len(reviews) % reviews_per_page == 0:
            last_cursor -= reviews_per_page
        last_review_url = url_for('user_bp.profile', cursor=last_cursor)
    
    return render_template("userReview.html", 
    user=user, 
    reviews = reviews_to_be_displayed, 
    prev_track_url = prev_review_url,
    first_track_url = first_review_url,
    next_track_url = next_review_url,
    last_track_url = last_review_url,
    )

class ProfanityFree:
    def __init__(self, message=None):
        if not message:
            message = u'Field must not contain profanity'
        self.message = message

    def __call__(self, form, field):
        if profanity.contains_profanity(field.data):
            raise ValidationError(self.message)


class PlaylistForm(FlaskForm):
    playlist = StringField('Review', [
        DataRequired(),
        Length(min=4, max=40, message='Please only use between 4 - 40 characters when naming your playlist'),
        ProfanityFree(message='Your name must not contain profanity')])
    submit = SubmitField('Submit')