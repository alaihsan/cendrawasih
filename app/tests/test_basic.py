import pytest
from app import create_app, db

@pytest.fixture
def app():
    app = create_app('development')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:password@localhost/db_cendrawasih'
    })

    with app.app_context():
        # Tables should be created by migrations in CI
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_page(client):
    """Test if index page loads correctly"""
    response = client.get('/')
    assert response.status_code == 200
    # Add more assertions if needed based on templates/index.html content
