"""Initialize Flask app."""
from pathlib import Path
from flask import Flask, render_template

# imports from SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from sqlalchemy.pool import NullPool

#Import adapter repositories
import music.adapters.repository as repo
from music.adapters.memory_repository import MemoryRepository, populate

def page_not_found(e):
    return render_template('404.html'), 404

def create_app(test_config=None):
    app = Flask(__name__)

    # Configure the app from configuration-file settings.
    app.config.from_object('config.Config')
    data_path = Path('music') / 'adapters' / 'data'

    if test_config is not None:
        # Load test configuration, and override any configuration settings.
        app.config.from_mapping(test_config)
        data_path = app.config['TEST_DATA_PATH']
    
    # Here the "magic" of our repository pattern happens. We can easily switch between in memory data and
    # persistent database data storage for our application.

    if app.config['REPOSITORY'] == 'memory':
        # Create the MemoryRepository implementation for a memory-based repository.
        repo.repo_instance = MemoryRepository()
        # fill the content of the repository from the provided csv files (has to be done every time we start app!)
        database_mode = False
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

        from .utilities import utilities
        app.register_blueprint(utilities.utilities_blueprint)

        from .tracks import review
        app.register_blueprint(review.review_blueprint)

        from .user import user
        app.register_blueprint(user.user_blueprint)

        app.register_error_handler(404, page_not_found)

    return app
