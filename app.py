from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import requests
import datetime
from dateutil.parser import parse
from time_interval import is_data_available

# Load environment variables
load_dotenv()
mongo_uri = os.getenv("PAUL_MONGO_URI")  # Change to JACK URI when deploying

# Initialize Flask app
app = Flask(__name__)

# Connect to MongoDB
client: MongoClient = MongoClient(mongo_uri)
# db = client["qubit_database"]  # Change to JACK URI database when deploying
# collection = db["company_news"]  # Change to JACK URI database when deploying
db = client["quant_data"]
collection = db["news_api"]
interval_collection = db["company_index"]

API_BASE_URL = "http://127.0.0.1:5000/company"

def convert_date_format(date_str):
    #date_obj = datetime.strptime(date_str, "%d-%m-%Y")
   # return datetime.fromisoformat(date_str.rstrip("Z")).strftime("%Y-%m-%d")
    #return date_obj.strftime("%Y-%m-%d")
    return parse(date_str).strftime("%Y-%m-%d")


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


@app.route("/company/<name>", methods=["GET"])
def get_company_news(name):
    query = {"$or": []}
    query["$or"].append({"attribute.title": {"$regex": name, "$options": "i"}})
    query["$or"].append(
        {"attribute.description": {"$regex": name, "$options": "i"}})

    limit = request.args.get("limit", default=10, type=int)
    start_date = request.args.get("start_date", default=None, type=str)
    end_date = request.args.get("end_date", default=None, type=str)


    # If both start_date and end_date are provided, apply the date range filter
    if start_date and end_date:
        date_filter = {}

        start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")

        # Parse end_date and extend to the end of the day (23:59:59.999)
        end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        # end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)

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

    time_intervals = interval_collection.find_one({"name": name}, {"_id": 0, "intervals": 1})

    data_availability = is_data_available(time_intervals, start_dt_str, end_dt_str)

    start = data_availability["start"]
    end = data_availability["end"]
    need = data_availability["need"]

    base_url = "http://example.com/newsapi"
    start_data = []
    needed_data = []
    end_data = []

    if (start == end and need == None) or (start is not None and end is None):
        # Only query the database
        start_dt = datetime.datetime.strptime(start[0], "%d-%m-%Y")
        end_dt = datetime.datetime.strptime(start[1], "%d-%m-%Y")
        date_filter = {"$gte": start_dt, "$lte": end_dt}
        query["time_object.timestamp"] = date_filter
        start_data = list(collection.find(query, {"_id": 0}).sort(
            "time_object.timestamp", -1).limit(limit))
    elif (start is None and end is not None):
        # query the database for the end
        start_dt = datetime.datetime.strptime(end[0], "%d-%m-%Y")
        end_dt = datetime.datetime.strptime(end[1], "%d-%m-%Y")
        date_filter = {"$gte": start_dt, "$lte": end_dt}
        query["time_object.timestamp"] = date_filter
        end_data = list(collection.find(query, {"_id": 0}).sort(
            "time_object.timestamp", -1).limit(limit))
        
    elif (start is not None and end is not None and need is not None and start != end):
        # query the database for start
        start_dt = datetime.datetime.strptime(start[0], "%d-%m-%Y")
        end_dt = datetime.datetime.strptime(start[1], "%d-%m-%Y")
        date_filter = {"$gte": start_dt, "$lte": end_dt}
        query["time_object.timestamp"] = date_filter
        start_data = list(collection.find(query, {"_id": 0}).sort(
            "time_object.timestamp", -1).limit(limit))
        # query the database for end
        start_dt = datetime.datetime.strptime(end[0], "%d-%m-%Y")
        end_dt = datetime.datetime.strptime(end[1], "%d-%m-%Y")
        date_filter = {"$gte": start_dt, "$lte": end_dt}
        query["time_object.timestamp"] = date_filter
        end_data = list(collection.find(query, {"_id": 0}).sort(
            "time_object.timestamp", -1).limit(limit))
        
        
    if (need is not None):
        params = {
            'name': name,
            'from_date': convert_date_format(need[0]),
            'to_date': convert_date_format(need[1])
        }
        # Send the GET request
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            needed_data = response.json().get("events")
    
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


if __name__ == "__main__":
    app.run(debug=True)