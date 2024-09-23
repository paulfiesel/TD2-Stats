import pytest
from app import app

@pytest.fixture
def client():
    # This is a test client for our Flask app
    with app.test_client() as client:
        yield client

def test_healthz(client):
    """Test the /healthz endpoint for a 200 status code and empty response body."""
    response = client.get('/healthz')
    assert response.status_code == 200
    assert response.data == b''