from datetime import date

from flask import Blueprint
from flask import request, render_template, redirect, url_for, session

import music.adapters.repository as repo
import music.utilities.utilities as utilities
import music.tracks.services as services
from music.utilities.utilities import create_search_form

#from music.authentication.authentication import login_required


# Configure Blueprint.
info_blueprint = Blueprint('info_bp', __name__)

@info_blueprint.route('/track/<int:track_id>', methods=['GET'])
def track(track_id: int):
    return render_template ('trackinfo.html')