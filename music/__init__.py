"""Initialize Flask app."""
from pathlib import Path
from flask import Flask, render_template


import music.adapters.repository as repo
from music.adapters.memory_repository import MemoryRepository, populate


def create_app(test_config=None):
    app = Flask(__name__)

    # Configure the app from configuration-file settings.
    app.config.from_object('config.Config')
    data_path = Path('music') / 'adapters' / 'data'

    if test_config is not None:
        # Load test configuration, and override any configuration settings.
        app.config.from_mapping(test_config)
        data_path = app.config['TEST_DATA_PATH']
    
    # Create the MemoryRepository implementation for a memory-based repository.
    repo.repo_instance = MemoryRepository()
    # fill the content of the repository from the provided csv files
    populate(data_path, repo.repo_instance)
    
    # Build the application - these steps require an application context.
    with app.app_context():
        # Register blueprints.
        from .home import home
        app.register_blueprint(home.home_blueprint)
    
        from .tracks import tracks
        app.register_blueprint(tracks.tracks_blueprint)
    
        from .authentication import authentication
        app.register_blueprint(authentication.authentication_blueprint)

        from .tracks import information
        app.register_blueprint(information.info_blueprint)

    '''
        from .utilities import utilities
        app.register_blueprint(utilities.utilities_blueprint)
    '''

    return app
