from crypt import methods
from flask import Blueprint, render_template
from music.domainmodel.track import Track
import music.utilities.utilities as utilities

home_blueprint = Blueprint('home_bp', __name__)


@home_blueprint.route('/', methods=["GET", "POST"])
def home():
    # Use Jinja to customize a predefined html page rendering the layout for showing a single track.
    return render_template('home.html')
