from sqlalchemy import select, inspect
from tests_db.configtest import database_engine

from music.adapters.orm import metadata

def test_database_populate_inspect_table_names(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    assert inspector.get_table_names() == ['albums', 'artists', 'genres', 'liked_tracks', 'playlists', 'reviews', 'track_genres', 'tracks', 'user_playlists', 'users']

def test_database_populate_select_all_genres(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_genres_table = inspector.get_table_names()[2]

    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_genres_table]])
        result = connection.execute(select_statement)

        all_genres_names = []
        for row in result:
            all_genres_names.append(row['genre'])

        assert len(all_genres_names) == 60

def test_database_populate_select_all_users(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_users_table = inspector.get_table_names()[4]

    with database_engine.connect() as connection:
        # query for records in table users
        select_statement = select([metadata.tables[name_of_users_table]])
        result = connection.execute(select_statement)

        all_users = []
        for row in result:
            all_users.append(row['user_name'])
        #No users get populated on startup
        assert all_users == []

def test_database_populate_select_all_track_genre(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_track_genres_table = inspector.get_table_names()[6]

    with database_engine.connect() as connection:
        # query for records in table comments
        select_statement = select([metadata.tables[name_of_track_genres_table]])
        result = connection.execute(select_statement)

        all_track_genres = []
        for row in result:
            if row['track_id'] == 20: all_track_genres.append(row['genre_id'])
        #Test the many to many relationship with track and genre. 
        assert all_track_genres == [76, 103]

def test_database_populate_select_all_articles(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_articles_table = inspector.get_table_names()[7]

    with database_engine.connect() as connection:
        # query for records in table articles
        select_statement = select([metadata.tables[name_of_articles_table]])
        result = connection.execute(select_statement)

        all_tracks = []
        for row in result:
            all_tracks.append((row['track_id'], row['title']))

        nr_articles = len(all_tracks)
        assert nr_articles == 2000

        assert all_tracks[0] == (2, 'Food')
