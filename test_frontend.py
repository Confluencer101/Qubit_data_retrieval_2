import pytest
from app import app as flask_app
import json
from unittest.mock import patch, MagicMock
import datetime


@pytest.fixture
def app():
    """Create a Flask test client for the app."""
    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def mock_auth_api_key():
    """Mock the auth_api_key function."""
    with patch('app.auth_api_key') as mock:
        mock.return_value = {"valid": True}
        yield mock


@pytest.fixture
def mock_mongo_client():
    """Mock the MongoDB client."""
    with patch('app.MongoClient') as mock:
        # Create mock collections
        mock_collection = MagicMock()
        mock_interval_collection = MagicMock()

        # Setup the database structure
        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda x: {
            "news_api": mock_collection,
            "company_index": mock_interval_collection
        }[x]

        mock_client = MagicMock()
        mock_client.__getitem__.return_value = mock_db

        mock.return_value = mock_client

        yield mock_client, mock_collection, mock_interval_collection


def test_index_page_get(client):
    """Test that the index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200

    # Check that the important elements are present
    content = response.data.decode('utf-8')
    assert 'Company News Finder' in content
    assert 'Search for the latest stock news about any company' in content
    assert '<form id="searchForm"' in content
    assert 'Enter company name' in content
    assert 'Enter your API key or leave blank for demo access' in content


@patch('app.requests.get')
def test_company_endpoint_api_call_needed(mock_requests_get, client, mock_auth_api_key, mock_mongo_client):
    """Test the /company/<name> endpoint when an API call is needed."""
    # Unpack the mock objects
    _, mock_collection, mock_interval_collection = mock_mongo_client

    # Set up test data for the API response
    api_response = {
        "events": [
            {
                "attribute": {
                    "title": "API News About Apple",
                    "description": "This is an API-sourced news article about Apple",
                    "publisher": "API Publisher",
                    "url": "http://example.com/news/api/1"
                },
                "time_object": {
                    "timestamp": datetime.datetime.now().isoformat()
                },
                "event_type": "News"
            }
        ]
    }

    # Configure the mocks
    mock_interval_collection.find_one.return_value = {
        "name": "Apple",
        "time_intervals": [
            ["01-01-2025", "01-02-2025"],
            ["01-04-2025", "01-05-2025"]
        ]
    }

    mock_collection.find.return_value.sort.return_value.limit.return_value = []

    # Mock the API response
    api_mock_response = MagicMock()
    api_mock_response.status_code = 200
    api_mock_response.json.return_value = api_response
    mock_requests_get.return_value = api_mock_response

    # Make the request with a date range that requires API data
    response = client.get(
        '/company/Apple?api_key=test_key&start_date=2025-01-01&end_date=2025-01-05')

    # Verify the response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "events" in data
    assert mock_requests_get.called


def test_company_endpoint_missing_api_key(client):
    """Test the /company/<name> endpoint without an API key."""
    response = client.get('/company/Apple')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert "API key is required" in data["error"]


@patch('app.auth_api_key')
def test_company_endpoint_invalid_api_key(mock_auth_api_key, client):
    """Test the /company/<name> endpoint with an invalid API key."""
    mock_auth_api_key.side_effect = Exception("API key validation failed 401")

    response = client.get('/company/Apple?api_key=invalid_key')
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    assert "API key validation failed" in data["error"]


@patch('app.requests.get')
def test_index_post_with_valid_data(mock_requests_get, client):
    """Test submitting the form with valid data."""
    # Mock the API response for the internal request
    api_mock_response = MagicMock()
    api_mock_response.status_code = 200
    api_mock_response.json.return_value = {
        "events": [
            {
                "attribute": {
                    "title": "Test News",
                    "description": "Description"
                },
                "time_object": {
                    "timestamp": datetime.datetime.now().isoformat()
                }
            }
        ]
    }
    mock_requests_get.return_value = api_mock_response

    # Submit the form
    response = client.post('/', data={
        'name': 'Apple',
        'start_date': '2025-01-01',
        'end_date': '2025-01-05'
    })

    # Check that we get a 200 response
    assert response.status_code == 200

    # Check that the mock was called
    assert mock_requests_get.called


def test_default_dates_are_set():
    """Test that default dates are set correctly in JavaScript."""
    # This is a bit tricky to test with pytest since it's client-side JS
    # We'll check that the script initializes the date values
    with flask_app.test_client() as client:
        response = client.get('/')
        content = response.data.decode('utf-8')

        # Verify the JS code sets default dates
        assert "startDateInput.value = formatDate(sevenDaysAgo);" in content
        assert "endDateInput.value = formatDate(today);" in content


def test_default_api_key_handling():
    """Test that default API key functionality is implemented."""
    with flask_app.test_client() as client:
        response = client.get('/')
        content = response.data.decode('utf-8')

        # Verify default API key constant is defined
        assert "const DEFAULT_API_KEY =" in content

        # Check toggling behavior
        assert "apiKeyInput.disabled = true;" in content
        assert "apiKeyInput.disabled = false;" in content
