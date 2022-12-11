import json
import os
from datetime import datetime
import time

from dotenv import load_dotenv
import requests

from utils.action_types import close, elicit_slot, elicit_intent
from utils.validation import validate_dining_suggestion
from utils.helpers import get_slot, get_session_attributes, mile_to_meter, price_to_dollar

load_dotenv()

HEADERS = {"Authorization": "bearer %s" % os.getenv("YELP_KEY")}


def welcome(intent_request):
    session_attributes = get_session_attributes(intent_request)
    fulfillment_state = "Fulfilled"
    message = {
        'contentType': 'PlainText',
        'content': 'This is your private dining concierge here. How can I help you today?'
    }

    return elicit_intent(intent_request, session_attributes, fulfillment_state, message)


def initial_search_yelp(intent_request, context):
    session_attributes = get_session_attributes(intent_request)

    # fetch slots
    location = get_slot(intent_request, "location")
    eat_now = get_slot(intent_request, "eat_now")
    if eat_now == "now":
        now = datetime.now()
        search_date = now.strftime("%Y-%m-%d")
        search_time = now.strftime("%H:%M")
    else:
        search_date = get_slot(intent_request, "date")
        search_time = get_slot(intent_request, "time")
    term = get_slot(intent_request, "term")
    people = get_slot(intent_request, "people")
    radius = get_slot(intent_request, "radius")
    price = get_slot(intent_request, "price")
    reserve = get_slot(intent_request, "reservation")

    # set request parameters
    params = {
        "location": location,
        "term": term,
        "radius": mile_to_meter(int(radius)),
        "price": price_to_dollar(int(price)),
        "limit": 5,
        "offset": 0
    }

    if eat_now == "now":
        params["open_now"] = True
    else:
        dt = datetime.strptime(search_date + "," + search_time, "%Y-%m-%d,%H:%M")
        params["open_at"] = int(time.mktime(dt.timetuple()))

    if reserve == "do":
        params["reservation_date"] = search_date
        params["reservation_time"] = search_time
        params["reservation_covers"] = int(people)

    response = requests.get(url=os.getenv("YELP_URL"), params=params, headers=HEADERS)
    all_businesses = response.json()
    nums = all_businesses["total"]

    if nums > 0:
        text = "I have found " + str(all_businesses["total"]) + " restaurants for you!"
        fulfillment_state = "Fulfilled"

    else:
        text = f"""Sorry, it seems no available restaurants around {location} that meet your requirements.
                   Please change some settings and try again."""
        fulfillment_state = "Failed"

    message = {
        'contentType': 'PlainText',
        'content': text
    }
    additional_info = all_businesses["businesses"]

    return close(intent_request, session_attributes, fulfillment_state, message, additional_info)


