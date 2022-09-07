"""Initialize Flask app."""
from pathlib import Path
from flask import Flask, render_template

# TODO: Access to the tracks should be implemented via the repository pattern and using blueprints, so this can not
#  stay here!
from music.domainmodel.track import Track
'''import music.adapters.repository as repo
from music.adapters.memory_repository import MemoryRepository, populate'''


# TODO: Access to the tracks should be implemented via the repository pattern and using blueprints, so this can not
#  stay here!
def create_some_track():
    some_track = Track(1, "Heat Waves")
    some_track.track_duration = 250
    some_track.track_url = 'https://spotify/track/1'
    return some_track


def create_app(test_config=None):
    app = Flask(__name__)

    # Configure the app from configuration-file settings.
    app.config.from_object('config.Config')
    data_path = Path('music') / 'adapters' / 'data'

    if test_config is not None:
        # Load test configuration, and override any configuration settings.
        app.config.from_mapping(test_config)
        data_path = app.config['TEST_DATA_PATH']
    
    '''# Create the MemoryRepository implementation for a memory-based repository.
    repo.repo_instance = MemoryRepository()
    # fill the content of the repository from the provided csv files
    populate(data_path, repo.repo_instance)'''
    
    # Build the application - these steps require an application context.
    '''
    with app.app_context():
        # Register blueprints.
        from .home import home
        app.register_blueprint(home.home_blueprint)

        from .news import news
        app.register_blueprint(news.news_blueprint)

        from .authentication import authentication
        app.register_blueprint(authentication.authentication_blueprint)

        from .utilities import utilities
        app.register_blueprint(utilities.utilities_blueprint)
    '''

    @app.route('/')
    def home():
        some_track = create_some_track()
        # Use Jinja to customize a predefined html page rendering the layout for showing a single track.
        return render_template('layout.html')
    
    @app.route('/home')
    def new():
        some_track = create_some_track()
        # Use Jinja to customize a predefined html page rendering the layout for showing a single track.
        return render_template('home.html')

    return app
