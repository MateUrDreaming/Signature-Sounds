from datetime import date
from typing import Union

from flask import Blueprint, abort
from flask import request, render_template, redirect, url_for, session, abort

from better_profanity import profanity
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError

import music.adapters.repository as repo
import music.utilities.utilities as utilities
import music.tracks.services as services
from music.utilities.utilities import create_playlist_form, PlaylistForm
from music.authentication.authentication import login_required
import music.authentication.services as auth

#from music.authentication.authentication import login_required


# Configure Blueprint.
info_blueprint = Blueprint('info_bp', __name__)

@info_blueprint.route('/track/<int:track_id>', methods=['GET'])
def track(track_id: int):
    user=None
    try:
        track = services.get_track_by_id(int(track_id), repo.repo_instance)
        object = services.get_track_object_by_id(int(track_id), repo.repo_instance)
    except ValueError:
        abort(404)

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

    form = create_playlist_form(repo.repo_instance)


    return render_template ('trackinfo.html',
    track=track,
    user=user,
    object=object,
    form = form
    )

@info_blueprint.route('/track/liked', defaults={'track_id': None})
@info_blueprint.route('/track/liked/<int:track_id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def liked(track_id: Union[int, None]):
    user=None
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

    if request.method in ['POST']:
        try:
            track = services.get_track_object_by_id(int(track_id), repo.repo_instance)
        except ValueError:
            abort(404)

    if track not in user.liked_tracks:
        services.add_track_to_likes(repo.repo_instance, user, track)
        return redirect(request.referrer)
    elif track in user.liked_tracks:
        services.remove_track_from_likes(repo.repo_instance, user, track)
        return redirect(request.referrer)

    
@info_blueprint.route('/playlist/<int:track_id>', methods=['POST'])
@login_required
def add_to_playlist(track_id: Union[int, None]):
   
    user=None
 
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

    form = create_playlist_form(repo.repo_instance)
    if form.validate_on_submit():
        # Use the service layer to store the new review.
        services.add_playlist(repo.repo_instance, track_id, form.playlist.data)
        # Reload the page to show the new review
        return redirect(url_for('info_bp.track', track_id=track_id))


    return redirect(url_for('info_bp.track', track_id=track_id))
    
@info_blueprint.route('/user/<int:playlist_id>/<int:track_id>', methods=['POST'])
@login_required
def remove_playlist(playlist_id, track_id):
    
    user=None
 
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
    
    services.remove_playlist(repo.repo_instance, track_id, playlist_id)

    return redirect(url_for('user_bp.playlistID', playlist_id=playlist_id)) 
