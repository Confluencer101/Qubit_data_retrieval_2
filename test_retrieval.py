import pytest
from app import app
import re


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# Test: Get company news for a specific company


def test_get_company_news(client):
    company_name = "Apple"
    response = client.get(f"/company/{company_name}?api_key=hrppk6zHXrrFYM3CHqx0_Q)")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data['events'], list)
    # Ensure that there is at least one article returned
    assert len(data['events']) > 0

    # Check if either the title or description contains the company name (case-insensitive)
    for article in data['events']:
        title = article["attribute"]["title"]
        description = article["attribute"]["description"]

        # Use re.search to allow for partial matches (not just exact matches)
        title_match = re.search(
            r'\b' + re.escape(company_name) + r'\b', title, re.I)
        description_match = re.search(
            r'\b' + re.escape(company_name) + r'\b', description, re.I)

<<<<<<< HEAD
def test_get_company_news_case_insensitive(client):
    response = client.get("/company/oPTuS?api_key=hrppk6zHXrrFYM3CHqx0_Q")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0  # Optus exists in MongoDB test data
    title = data[0]["attribute"]["title"]
    description = data[0]["attribute"]["description"]
    assert re.search("Optus", title, re.I) or re.search(
        "Optus", description, re.I)

# Test: Get company news for a company with a date range (+ case insensitivity)


def test_get_company_news_range(client):
    response = client.get(
        "/company/aPPLe/range?api_key=hrppk6zHXrrFYM3CHqx0_Q&start_date=2025-03-07&end_date=2025-03-09")
    assert response.status_code == 200
    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) > 0  # At least one result should be returned

    # Check if the returned dates fall in range
    for article in data:
        print(article["time_object"]["timestamp"])
        # published_date = datetime.fromisoformat(article["time_object"]["timestamp"]).replace(tzinfo=pytz.utc)
        # published_date = datetime.fromisoformat(article["time_object"]["timestamp"]).replace(tzinfo=pytz.utc)
        published_date = parser.parse(
            article["time_object"]["timestamp"]).replace(tzinfo=pytz.utc)
        # This should be in the correct ISO format
        assert datetime(2025, 3, 7, tzinfo=pytz.utc).date(
        ) <= published_date.date() <= datetime(2025, 3, 9, tzinfo=pytz.utc).date()
=======
        # Ensure either title or description contains the company name
        assert title_match or description_match, f"Company name '{company_name}' not found in title or description"
>>>>>>> adding_timeInterval

# Test: Get company news with no results (company name does not exist)


def test_get_company_news_not_found(client):
<<<<<<< HEAD
    response = client.get(
        "/company/ThisCompanyDoesNotExist?api_key=hrppk6zHXrrFYM3CHqx0_Q")
    assert response.status_code == 404
    data = response.get_json()
    assert data["message"] == "No news found for ThisCompanyDoesNotExist"

# Test: Get company news with no results in a given date range


def test_get_company_news_range_not_found(client):
    response = client.get(
        "/company/Apple/range?api_key=hrppk6zHXrrFYM3CHqx0_Q&start_date=2020-01-01&end_date=2020-01-02")
    assert response.status_code == 404
    data = response.get_json()
    assert data["message"] == "No news found for Apple in the given date range"
=======
    response = client.get("/company/ThisCompanyDoesNotExist?api_key=hrppk6zHXrrFYM3CHqx0_Q")
    assert response.status_code == 404
    data = response.get_json()
    assert data["message"] == "No news found for ThisCompanyDoesNotExist in the past week"
>>>>>>> adding_timeInterval
