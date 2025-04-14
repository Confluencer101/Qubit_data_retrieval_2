from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import requests
import datetime
from dateutil.parser import parse
from time_interval import is_data_available
import re

# Load environment variables
load_dotenv()
mongo_uri = os.getenv("JACK_MONGO_URI")

# Initialize Flask app
app = Flask(__name__)

# Connect to MongoDB
client: MongoClient = MongoClient(mongo_uri)
db = client["quant_data"]
collection = db["news_api"]
interval_collection = db["company_index"]

API_BASE_URL = "http://170.64.135.87/newsapi"
COMPANY_TICKER_URL = "http://170.64.135.87/convert/company_to_ticker"
TICKER_COMPANY_URL = "http://170.64.135.87/convert/ticker_to_company"


def convert_date_format(date_str):
    return parse(date_str, dayfirst=True).strftime("%Y-%m-%d")


def auth_api_key(api_key):
    auth_url = 'http://170.64.139.10:8080/validate'
    data = {
        'apiKey': api_key
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(auth_url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return Exception(f"API key validation failed {response.status_code}")

# Function to authenticate:


@app.route('/', methods=['GET', 'POST'])
def index():
    news = None
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        if not name:
            error = "Company name is required."
        else:
            url = f"/company/{name}"
            params = {}

            if start_date and end_date:
                params['start_date'] = start_date
                params['end_date'] = end_date

            try:
                # Make an internal request to your own API
                api_url = request.host_url.rstrip('/') + url
                response = requests.get(api_url, params=params)
                response.raise_for_status()
                news = response.json()
            except requests.exceptions.RequestException as e:
                error = f"Error fetching company news: {str(e)}"

    return render_template('index.html', news=news, error=error)


@app.route("/company/<name>", methods=["GET"])
def get_company_news(name):
    try:
        api_key = request.args.get('api_key')
        if not api_key:
            return jsonify({"error": "API key is required"}), 400
        auth_api_key(api_key)
    except Exception as e:
        error_msg = str(e)
        status_code = 401 if "API key validation failed" in error_msg else 403
        return jsonify({"error": error_msg}), status_code

    query = {"$or": []}
    query["$or"].append({"attribute.title": {"$regex": name, "$options": "i"}})
    query["$or"].append(
        {"attribute.description": {"$regex": name, "$options": "i"}})

    limit = request.args.get("limit", default=10, type=int)
    start_date = request.args.get("start_date", default=None, type=str)
    end_date = request.args.get("end_date", default=None, type=str)

    # If both start_date and end_date are provided, apply the date range filter
    if start_date and end_date:
        start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    else:
        # If either start_date or end_date is missing, default to one week before today and today's date
        time_now = datetime.datetime.now()
        # One week before today
        start_dt = time_now - datetime.timedelta(days=7)
        # Today's date
        end_dt = time_now

    ###########################################################################################################################
    # THE NEW LOGIC GOES HERE
    start_dt_str = start_dt.strftime('%d-%m-%Y')
    end_dt_str = end_dt.strftime('%d-%m-%Y')

    # Get time intervals for the company
    company_data = interval_collection.find_one({"name": name.strip().lower()})
    time_intervals = company_data.get(
        "time_intervals", []) if company_data else []

    # Check data availability
    data_availability = is_data_available(
        time_intervals, start_dt_str, end_dt_str)

    start = data_availability["start"]
    end = data_availability["end"]
    need = data_availability["need"]

    start_data = []
    needed_data = []
    end_data = []

    # Case 1: Only query the database - data fully available
    if (start == end and need is None) or (start is not None and end is None):
        start_dt = datetime.datetime.strptime(start[0], "%d-%m-%Y")
        end_dt = datetime.datetime.strptime(start[1], "%d-%m-%Y")
        date_filter = {"$gte": start_dt, "$lte": end_dt}
        query["time_object.timestamp"] = date_filter
        start_data = list(collection.find(query, {"_id": 0}).sort(
            "time_object.timestamp", -1).limit(limit))

    # Case 2: Only the end portion is available
    elif start is None and end is not None:
        start_dt = datetime.datetime.strptime(end[0], "%d-%m-%Y")
        end_dt = datetime.datetime.strptime(end[1], "%d-%m-%Y")
        date_filter = {"$gte": start_dt, "$lte": end_dt}
        query["time_object.timestamp"] = date_filter
        end_data = list(collection.find(query, {"_id": 0}).sort(
            "time_object.timestamp", -1).limit(limit))

    # Case 3: Both start and end portions available, but need middle portion
    elif start is not None and end is not None and need is not None and start != end:
        # Query for start portion
        start_dt = datetime.datetime.strptime(start[0], "%d-%m-%Y")
        end_dt = datetime.datetime.strptime(start[1], "%d-%m-%Y")
        date_filter = {"$gte": start_dt, "$lte": end_dt}
        query["time_object.timestamp"] = date_filter
        start_data = list(collection.find(query, {"_id": 0}).sort(
            "time_object.timestamp", -1).limit(limit))

        # Query for end portion
        start_dt = datetime.datetime.strptime(end[0], "%d-%m-%Y")
        end_dt = datetime.datetime.strptime(end[1], "%d-%m-%Y")
        date_filter = {"$gte": start_dt, "$lte": end_dt}
        query["time_object.timestamp"] = date_filter
        end_data = list(collection.find(query, {"_id": 0}).sort(
            "time_object.timestamp", -1).limit(limit))

    # Handle missing data - make API call
    if need is not None:
        from_date = convert_date_format(need[0])
        to_date = convert_date_format(need[1])

        # Construct API request
        params = {
            'name': name,
            'from_date': from_date,
            'to_date': to_date
        }

        # Send the GET request to external API
        try:
            response = requests.get(API_BASE_URL, params=params)
            response.raise_for_status()  # Raise exception for non-200 status codes

            # Try to parse JSON response
            response_data = response.json()

            # Check the structure of the response
            if isinstance(response_data, dict) and "events" in response_data:
                needed_data = response_data["events"]
            else:
                needed_data = response_data if isinstance(
                    response_data, list) else []

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from API: {str(e)}")
            needed_data = []
        except ValueError as e:  # JSON parsing error
            print(f"Error parsing API response: {str(e)}")
            needed_data = []

    # Combine all data
    finalEvents = start_data + needed_data + end_data

    ###########################################################################################################################

    if not finalEvents:
        if start_date and end_date:
            return jsonify({"message": f"No news found for {name} in the given date range"}), 404
        else:
            return jsonify({"message": f"No news found for {name} in the past week"}), 404

    company_news = {
        'data_source': 'news_api_org',
        'dataset_id': '1',
        'dataset_type': 'News data',
        'events': finalEvents
    }
    return jsonify(company_news), 200


@app.route('/convert/company_to_ticker')
def convert_company_to_ticker():
    name = request.args.get('name')

    if not name or not re.match(r'^[a-zA-Z\s]+$', name):
        return jsonify({"error": "Invalid 'name' given"}), 400
    
    params = {
        'name': name
    }
    
    try:
        response = requests.get(API_BASE_URL, params=params)
        response.raise_for_status()  # Raise exception for non-200 status codes
        response_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

    return jsonify(response_data), 200


@app.route('/convert/ticker_to_company')
def convert_ticker_to_company():
    ticker = request.args.get('ticker')

    if not ticker:
        return jsonify({"error": "Invalid 'ticker' given"}), 400

    params = {
        'ticker': ticker
    }
    
    try:
        response = requests.get(API_BASE_URL, params=params)
        response.raise_for_status()  # Raise exception for non-200 status codes
        response_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

    return jsonify(response_data), 200


if __name__ == "__main__":
    app.run(debug=True)
