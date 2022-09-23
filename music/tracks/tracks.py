from datetime import date

from flask import Blueprint
from flask import request, render_template, redirect, url_for, session, abort

import music.adapters.repository as repo
import music.utilities.utilities as utilities
import music.tracks.services as services
from music.utilities.utilities import create_search_form

#from music.authentication.authentication import login_required


# Configure Blueprint.
tracks_blueprint = Blueprint('tracks_bp', __name__)

@tracks_blueprint.route('/search', methods=['GET'])
def search():
    #initial values
    valid_query = False
    tracks_per_page = 25
    first_track_url = None
    last_track_url = None
    next_track_url = None
    prev_track_url = None
    valid_types = ["query", "artists", "genres", "albums", None]

    type= request.args.get('type')
    query = request.args.get('query')
    cursor = request.args.get('cursor')
    
    if type not in valid_types:
        abort(404)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    

    # Retrieve track ids for tracks that are associated with the query.
    track_ids = services.get_track_ids_for_query(query, type, repo.repo_instance)
    
    if cursor < 0 or cursor > len(track_ids): cursor = 0
    
    cursor = (cursor // tracks_per_page) * 25

    # Retrieve the batch of tracls to display on the Web page.
    tracks = services.get_tracks_by_id(track_ids[cursor:cursor + tracks_per_page], repo.repo_instance)
    
    
    if cursor > 0:
        # There are preceding articles, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_track_url = url_for('tracks_bp.search', query=query, type=type, cursor=cursor - tracks_per_page)
        first_track_url = url_for('tracks_bp.search', query=query, type=type)


    if cursor + tracks_per_page < len(track_ids):
        # There are further articles, so generate URLs for the 'next' and 'last' navigation buttons.
        next_track_url = url_for('tracks_bp.search', query=query, type=type, cursor=cursor + tracks_per_page)
    
        last_cursor = tracks_per_page * int(len(track_ids) / tracks_per_page)
        if len(track_ids) % tracks_per_page == 0:
            last_cursor -= tracks_per_page
        last_track_url = url_for('tracks_bp.search', query=query, type=type, cursor=last_cursor)
    
    if query: tracks_title = "All tracks associated with" + query
    else: tracks_title = "All tracks"

    # Use Jinja to customize a predefined html page rendering the layout for showing a single track.
    return render_template (
        'find_tracks.html',
        tracks_title = tracks_title,
        tracks = tracks,
        first_track_url=first_track_url,
        last_track_url=last_track_url,
        prev_track_url=prev_track_url,
        next_track_url=next_track_url,
        cursor=cursor,
        total_leng = len(track_ids),
        leng = len(tracks),
        form = utilities.create_search_form(repo, request.args)
    )

