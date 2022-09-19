from datetime import date

from flask import Blueprint, abort
from flask import request, render_template, redirect, url_for, session, abort

from better_profanity import profanity
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError

import music.adapters.repository as repo
import music.utilities.utilities as utilities
import music.tracks.services as services
from music.utilities.utilities import create_search_form
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
    except ValueError:
        abort(404)

    try:
        user = auth.get_user(repo, session['username'])
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


    return render_template ('trackinfo.html',
    track=track,
    user=user
    )

@info_blueprint.route('/review/<int:track_id>', methods=['GET', 'POST'])
def review(track_id: int):
    sesh=False
    user=None
    reviews_per_page = 3
    first_review_url = None
    last_review_url = None
    next_review_url = None
    prev_review_url = None

    try:
        track = services.get_track_by_id(int(track_id), repo.repo_instance)
    except ValueError:
        abort(404)
    
    try:
        user = auth.get_user(session['user_name'], repo.repo_instance)['user_name']
        sesh = True
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

    reviews = services.get_reviews(repo.repo_instance, track)
    
    form = ReviewForm()
    if form.validate_on_submit() and sesh:
        # Use the service layer to store the new review.
        services.add_review(repo.repo_instance, track, form.review.data, form.rating.data, user)
        # Reload the page to show the new review
        return redirect(url_for('info_bp.review', track_id=track_id))
    
    if request.method == 'POST':
        review_error_message = 'Invalid review.'
    
    cursor = request.args.get('cursor')

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)
    
    reviews_to_be_displayed = reviews[cursor:cursor + reviews_per_page]
    
    if cursor > 0:
        # There are preceding articles, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_review_url = url_for('info_bp.review', track_id=track_id, cursor=cursor - reviews_per_page)
        first_review_url = url_for('info_bp.review', track_id=track_id)

    

    if cursor + reviews_per_page < len(reviews):
        # There are further articles, so generate URLs for the 'next' and 'last' navigation buttons.
        next_review_url = url_for('info_bp.review', track_id=track_id, cursor=cursor + reviews_per_page)
    
        last_cursor = reviews_per_page * int(len(reviews) / reviews_per_page)
        if len(reviews) % reviews_per_page == 0:
            last_cursor -= reviews_per_page
        last_review_url = url_for('info_bp.review', track_id=track_id, cursor=last_cursor)
    

    return render_template ('review.html', 
    track=track,
    user=user,
    sesh=sesh,
    form=form, 
    reviews = reviews_to_be_displayed,
    leng = len(reviews),
    prev_track_url = prev_review_url,
    first_track_url = first_review_url,
    next_track_url = next_review_url,
    last_track_url = last_review_url
    )



class ProfanityFree:
    def __init__(self, message=None):
        if not message:
            message = u'Field must not contain profanity'
        self.message = message

    def __call__(self, form, field):
        if profanity.contains_profanity(field.data):
            raise ValidationError(self.message)


class ReviewForm(FlaskForm):
    rating = SelectField(
        'Rating',
        [DataRequired(message="A rating must be selected!"),
        NumberRange(min=1, max=5, message="select number between 1 and 5")],
        choices=range(1, 6),
        coerce=int,
        default=5)
    review = TextAreaField('Review', [
        DataRequired(),
        Length(min=20, max=2000, message='Please only use between 20 - 2000 characters when writing your review'),
        ProfanityFree(message='Your comment must not contain profanity')])
    submit = SubmitField('Submit')