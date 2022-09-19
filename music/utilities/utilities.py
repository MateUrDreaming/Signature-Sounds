from flask import Blueprint, request, render_template, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField

from music.adapters.repository import AbstractRepository
import music.utilities.services as services


# Configure Blueprint.
utilities_blueprint = Blueprint('utilities_bp', __name__)

def create_search_form(repo: AbstractRepository, request_args):
    """ Returns a MovieSearchForm populated with options from the given repository. """

    form = MovieSearchForm(request_args, meta={'csrf': False})
    form.type.choices = [("query", "Track"), ("artists", "Artists"), ("genres", "Genres"), ("albums", "Albums")] 

    return form

class MovieSearchForm(FlaskForm):
    query = StringField('query')
    type = SelectField('type')
    submit = SubmitField('Submit')