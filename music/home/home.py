from flask import Blueprint, render_template, request, redirect, url_for, session
from music.domainmodel.track import Track
import music.adapters.repository as repo
import music.utilities.utilities as utilities

home_blueprint = Blueprint('home_bp', __name__)


@home_blueprint.route('/')
def home():
    # Use Jinja to customize a predefined html page rendering the layout for showing a single track.
    return render_template('home.html', form=utilities.create_search_form(repo, request.args))
