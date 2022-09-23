from flask import Blueprint, request, render_template, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField

from music.adapters.repository import AbstractRepository
import music.utilities.services as services


# Configure Blueprint.
utilities_blueprint = Blueprint('utilities_bp', __name__)

def create_search_form(repo: AbstractRepository, request_args):
    """ Returns a trackSearchForm populated with valid types. """

    form = trackSearchForm(request_args, meta={'csrf': False})
    form.type.choices = [("query", "Track"), ("artists", "Artists"), ("genres", "Genres"), ("albums", "Albums")] 

    return form

def create_playlist_form(repo: AbstractRepository):
    """ Returns a MovieSearchForm populated with options from the given repository. """

    form = PlaylistForm()
    form.playlist.choices = [(playlist.list_id, playlist.title) for playlist in repo.get_all_playlist()] 

    return form

class trackSearchForm(FlaskForm):
    query = StringField('query')
    type = SelectField('type')
    submit = SubmitField('Submit')



class PlaylistForm(FlaskForm):
    playlist = SelectField('Playlist')
    submit = SubmitField('Submit')