import pytest
from flask import Flask
from app import app  # Import the Flask app from your main application file

# Flask-Testing client fixture


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# Test: GET request to index route


def test_get_index(client):
    response = client.get('/')
    assert response.status_code == 200
    # Check if the form has a Company Name field
    assert b"Company Name" in response.data
    # Check if the form has a Start Date field
    assert b"Start Date" in response.data
    assert b"End Date" in response.data  # Check if the form has an End Date field
    assert b"Get News" in response.data  # Check if the submit button exists


# Test: POST request with missing stock symbol


def test_post_missing_symbol(client):
    response = client.post('/', data={
        'symbol': '',
        'start_date': '',
        'end_date': ''
    })
    assert response.status_code == 200
    # Check if error message is shown
    assert b"Company name is required." in response.data


# Test: POST request with invalid stock symbol


def test_post_invalid_symbol(client):
    response = client.post('/', data={
        'name': 'ThisCompanyDoesNotExist',
        'start_date': '2025-03-01',
        'end_date': '2025-03-10'
    })
    assert response.status_code == 200
    # Check if error message is shown
    assert b"Error fetching company news" in response.data
