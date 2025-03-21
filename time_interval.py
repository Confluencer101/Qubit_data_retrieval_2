from datetime import datetime, timedelta



def add_one_day(date_str):
    # Convert the input string to a datetime object
    date_obj = datetime.strptime(date_str, "%d-%m-%Y")
    
    # Add one day using timedelta
    new_date = date_obj + timedelta(days=1)
    
    # Convert the datetime object back to string in the same format
    return new_date.strftime("%d-%m-%Y")

def subtract_one_day(date_str):
    # Convert the input string to a datetime object
    date_obj = datetime.strptime(date_str, "%d-%m-%Y")
    
    # Subtract one day using timedelta
    new_date = date_obj - timedelta(days=1)
    
    # Convert the datetime object back to string in the same format
    return new_date.strftime("%d-%m-%Y")


def is_data_available(intervals, start_date_str, end_date_str):
    iHave = []
    iNeedToRequest = []
    
    # Convert string date to datetime objects for easier comparison
    start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
    end_date = datetime.strptime(end_date_str, "%d-%m-%Y")
    
    # Loop through the intervals to check for overlaps and gaps
    existing_start = None
    existing_end = None
    need = None
    
    for interval in intervals:
        # Convert stored intervals to datetime objects
        stored_start = datetime.strptime(interval[0], "%d-%m-%Y")
        stored_end = datetime.strptime(interval[1], "%d-%m-%Y")

        if stored_start <= start_date and start_date <= stored_end:
            existing_start = [start_date_str, interval[1]]
        if stored_start <= end_date and end_date <= stored_end:
            existing_end = [interval[0], end_date_str]

    if (existing_start and existing_end and 
        (datetime.strptime(existing_end[0], "%d-%m-%Y") < datetime.strptime(existing_start[0], "%d-%m-%Y")) and
        (datetime.strptime(existing_end[1], "%d-%m-%Y") < datetime.strptime(existing_start[1], "%d-%m-%Y"))):
        existing_start = [existing_start[0], existing_end[1]]
        existing_end = existing_start
        need = None
    elif (existing_start and existing_end):
        need = [add_one_day(existing_start[1]), subtract_one_day(existing_end[0])]
    elif (existing_start and (not existing_end)):
        need = [add_one_day(existing_start[1]), end_date_str]
    elif ((not existing_start) and existing_end):
        need = [start_date_str, subtract_one_day(existing_end[0])]
    else:
        need = [start_date_str, end_date_str]
    
    return {"start": existing_start, "end": existing_end, "need": need}


# # Example usage:
# # this would be requested from the database.
# intervals = []



# # The use of is_data_available will only need to be done by data_retrival

# # Query for data from 2020-01-01 to 2024-12-31
# result = is_data_available(intervals, '01-01-2020', '31-12-2024')

# print(result)
