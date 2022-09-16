from flask import Blueprint, render_template
from music.domainmodel.track import Track
import music.utilities.utilities as utilities

def create_some_track():
    some_track = Track(1, "Heat Waves")
    some_track.track_duration = 250
    some_track.track_url = 'https://spotify/track/1'
    return some_track

home_blueprint = Blueprint('home_bp', __name__)


@home_blueprint.route('/', methods=['GET'])
def home():
    some_track = create_some_track()
    # Use Jinja to customize a predefined html page rendering the layout for showing a single track.
    return render_template('simple_track.html', 
            tracks = utilities.get_track_titles())
