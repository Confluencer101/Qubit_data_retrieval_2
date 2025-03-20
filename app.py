from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import requests
import datetime

# Load environment variables
load_dotenv()
mongo_uri = os.getenv("JACK_MONGO_URI")  # Change to JACK URI when deploying

# Initialize Flask app
app = Flask(__name__)

# Connect to MongoDB
client: MongoClient = MongoClient(mongo_uri)
# db = client["qubit_database"]  # Change to JACK URI database when deploying
# collection = db["company_news"]  # Change to JACK URI database when deploying
db = client["quant_data"]
collection = db["news_api"]

API_BASE_URL = "http://127.0.0.1:5000/company"


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
            params = {"name": name.upper()}

            if start_date and end_date:
                url = f"{API_BASE_URL}/{name}/range"
                params['start_date'] = start_date
                params['end_date'] = end_date
            else:
                url = f"{API_BASE_URL}/{name}"

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                news = response.json()
            except requests.exceptions.RequestException as e:
                error = f"Error fetching company news: {str(e)}"

    return render_template('index.html', news=news, error=error)

# GET latest news for a specific company (no date filtering)


@app.route("/company/<name>", methods=["GET"])
def get_company_news(name):
    query = {"$or": []}
    query["$or"].append({"attribute.title": {"$regex": name, "$options": "i"}})
    query["$or"].append({"attribute.description": {"$regex": name, "$options": "i"}})

    limit = request.args.get("limit", default=10, type=int)

    company_news = list(collection.find(query, {"_id": 0}).sort(
        "time_object.timestamp", -1).limit(limit))

    if not company_news:

        return jsonify({"message": f"No news found for {name}"}), 404

    return jsonify(company_news), 200

# GET news for a specific company within a date range


@app.route("/company/<name>/range", methods=["GET"])
def get_company_news_range(name):
    query = {"$or": []}
    query["$or"].append({"attribute.title": {"$regex": name, "$options": "i"}})
    query["$or"].append({"attribute.description": {"$regex": name, "$options": "i"}})

    limit = request.args.get("limit", default=10, type=int)

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if start_date or end_date:
        date_filter = {}
        if start_date:
            start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            date_filter["$gte"] = start_dt
        if end_date:
            # Parse end_date and extend to the end of the day
            end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            end_dt = end_dt.replace(
                hour=23, minute=59, second=59, microsecond=999999)
            # End of the day: 2025-03-15 23:59:59.999
            date_filter["$lte"] = end_dt
        query["time_object.timestamp"] = date_filter

    company_news = list(collection.find(query, {"_id": 0}).sort(
        "time_object.timestamp", -1).limit(limit))

    if not company_news:
        return jsonify({"message": f"No news found for {name} in the given date range"}), 404

    return jsonify(company_news), 200


if __name__ == "__main__":
    app.run(debug=True)
