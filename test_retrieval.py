import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# Test: Get company news for a specific company


# def test_get_company_news(client):
#     company_name = "Apple"
#     response = client.get(
#         f"/company/{company_name}?api_key=hrppk6zHXrrFYM3CHqx0_Q)")
#     assert response.status_code == 200
#     data = response.get_json()
#     assert isinstance(data['events'], list)
#     # Ensure that there is at least one article returned
#     assert len(data['events']) > 0

#     # Check if either the title or description contains the company name (case-insensitive)
#     for article in data['events']:
#         title = article["attribute"]["title"]
#         description = article["attribute"]["description"]

#         # Use re.search to allow for partial matches (not just exact matches)
#         title_match = re.search(
#             r'\b' + re.escape(company_name) + r'\b', title, re.I)
#         description_match = re.search(
#             r'\b' + re.escape(company_name) + r'\b', description, re.I)

#         # Ensure either title or description contains the company name
#         assert title_match or description_match, f"Company name {company_name} not found in title or description"

# Test: Get company news with no results (company name does not exist)


def test_get_company_news_not_found(client):
    response = client.get(
        "/company/ThisCompanyDoesNotExist?api_key=hrppk6zHXrrFYM3CHqx0_Q")
    assert response.status_code == 404
    data = response.get_json()
    assert data["message"] == "No news found for ThisCompanyDoesNotExist in the past week"

def test_company_to_ticker(client):
    test_cases = [
        ["apple", "AAPL"],
        ["google", "GOOG"],
        ["microsoft", "MSFT"],
        ["facebook", "META"],
        ["adobe", "ADBE"],
        ["amazon", "AMZN"],
        ["tesla", "TSLA"],
        ["atlassian", "TEAM"]
    ]

    for case in test_cases:
        response = client.get(f"/convert/company_to_ticker?name={case[0]}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["ticker"] == case[1]

def test_company_to_ticker_no_name(client):
    response = client.get("/convert/company_to_ticker")
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid 'name' given"

def test_ticker_to_company(client):
    test_cases = [
        ["AAPL", "apple", "Apple Inc."],
        ["MSFT", "microsoft", "Microsoft Corporation"],
        ["ADBE", "adobe", "Adobe Inc."],
        ["AMZN", "amazon", "Amazon.com, Inc."],
        ["TSLA", "tesla", "Tesla, Inc."],
        ["TEAM", "atlassian", "Atlassian Corporation"]
    ]

    for case in test_cases:
        response = client.get(f"/convert/ticker_to_company?ticker={case[0]}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["short_name"] == case[1]
        assert data["full_name"] == case[2]

def test_ticker_to_company_no_ticker(client):
    response = client.get("/convert/ticker_to_company")
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid 'ticker' given"
