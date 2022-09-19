from datetime import date

from flask import Blueprint, abort
from flask import request, render_template, redirect, url_for, session, abort

import music.adapters.repository as repo
import music.utilities.utilities as utilities
import music.tracks.services as services
from music.utilities.utilities import create_search_form

#from music.authentication.authentication import login_required


# Configure Blueprint.
info_blueprint = Blueprint('info_bp', __name__)

@info_blueprint.route('/track/<int:track_id>', methods=['GET'])
def track(track_id: int):
    try:
        track = services.get_track_by_id(int(track_id), repo.repo_instance)
    except ValueError:
        abort(404)

    return render_template ('trackinfo.html',
    track=track
    )