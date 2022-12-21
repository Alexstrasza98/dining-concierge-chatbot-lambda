import json
import os
from datetime import datetime
import time

from dotenv import load_dotenv
import requests

from utils.action_types import close, elicit_slot, elicit_intent
from utils.helpers import get_slot, get_session_attributes, get_request_attributes, mile_to_meter, price_to_dollar

load_dotenv()

HEADERS = {"Authorization": "bearer %s" % os.getenv("YELP_KEY")}


def welcome(intent_request):
    session_attributes = get_session_attributes(intent_request)
    fulfillment_state = "Fulfilled"
    message = {
        "contentType": "PlainText",
        "content": "This is your private dining concierge here. How can I help you today?"
    }

    return elicit_intent(intent_request, session_attributes, fulfillment_state, message)


def initial_search_yelp(intent_request, context):

    # use session attributes to store
    session_attributes = get_session_attributes(intent_request)
    if "offset" not in session_attributes:
        session_attributes["offset"] = 0

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
        "limit": 6,
        "offset": session_attributes["offset"]
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

    # call yelp api and get answer
    response = requests.get(url=os.getenv("YELP_URL"), params=params, headers=HEADERS)
    all_businesses = response.json()
    nums = all_businesses["total"]

    # organize response
    requests_attributes = get_request_attributes(intent_request)
    session_id = intent_request["sessionId"]

    # if found any restaurant, go to next step
    if nums > 0:
        messages = [{
            "contentType": "PlainText",
            "content": "I have found " + str(all_businesses["total"]) + " restaurants for you! Current offset: " + str(params["offset"])
        }]

        intent = {
            "confirmationState": "None",
            "name": "ViewSpecificRestaurant",
            "slots": {
                "businessID": None
            },
            "state": "InProgress"
        }

        slot_to_elicit = "businessID"

        requests_attributes["businesses"] = json.dumps(all_businesses["businesses"])

        # temporarily use session attributes to save intent request
        session_attributes["search_request"] = json.dumps(intent_request)

    # if not, return with failed fulfillment
    else:
        messages = [{
            "contentType": "PlainText",
            "content": f"""Sorry, it seems no available restaurants around {location} that meet your requirements.
                        Please change some settings and try again."""
        },
        {
            "contentType": "PlainText",
            "content": "Please start over by selecting the place you want to have food in."
        }]

        intent = {
            "confirmationState": "None",
            "name": "SearchRestuarants",
            "slots": {
                "location": None,
                "eat_now": None,
                "date": None,
                "time": None,
                "term": None,
                "people": None,
                "radius": None,
                "price": None,
                "reservation": None
            },
            "state": "InProgress"
        }

        slot_to_elicit = "location"

    return elicit_slot(session_attributes, intent, slot_to_elicit, messages, requests_attributes, session_id)


def view_specific_restaurant(intent_request, context):

    # fetch slot
    business_id = get_slot(intent_request, "businessID")

    # if user not interested:
    if business_id == "no":
        # TODO: save initial search params in client instead of in session attributes, which may increase latency
        session_attributes = get_session_attributes(intent_request)
        original_request = json.loads(session_attributes["search_request"])
        original_request["sessionState"]["sessionAttributes"]["offset"] += 6
        return initial_search_yelp(original_request, context)

    # if user click on one specific card
    else:
        business = requests.get(url=os.getenv("YELP_BUSINESS_URL") + business_id, headers=HEADERS)
        reviews = requests.get(url=os.getenv("YELP_BUSINESS_URL") + business_id + "/reviews",
                               params={"limit": 3},
                               headers=HEADERS)
        business_info = business.json()
        reviews_info = reviews.json()

        requests_attributes = get_request_attributes(intent_request)
        requests_attributes["business_info"] = json.dumps(business_info)
        requests_attributes["reviews_info"] = json.dumps(reviews_info)
        session_attributes = get_session_attributes(intent_request)
        session_id = intent_request["sessionId"]

        intent = {
            "confirmationState": "None",
            "name": "SaveRestaurant",
            "slots": {
                "save": None
            },
            "state": "InProgress"
        }

        messages = [{
            "contentType": "PlainText",
            "content": "Finished Searching for Business with ID: " + business_id
        },
        {
            "contentType": "PlainText",
            "content": "Current page should be a page about a specific restaurant. Do you like it or not?"
        }]

        return elicit_slot(session_attributes, intent, "save", messages, requests_attributes, session_id)


def save_restaurant(intent_request, context):
    save = get_slot(intent_request, "save")

    if save == "yes":
        # TODO: make post request to /usr/save, pass information about user and restaurant information

        requests_attributes = get_request_attributes(intent_request)
        session_attributes = get_session_attributes(intent_request)
        session_id = intent_request["sessionId"]

        intent = {
            "confirmationState": "None",
            "name": "ReserveRestaurant",
            "slots": {
                "reserve": None
            },
            "state": "InProgress"
        }

        messages = [{
            "contentType": "PlainText",
            "content": "You have saved this restaurant to your profile. Do you want to reserve it?"
        }]

        return elicit_slot(session_attributes, intent, "reserve", messages, requests_attributes, session_id)

    elif save == "no":
        # TODO: save initial search params in local instead of in session attributes, which may increase latency
        session_attributes = get_session_attributes(intent_request)
        original_request = json.loads(session_attributes["search_request"])
        return initial_search_yelp(original_request, context)


def reserve_restaurant(intent_request, context):
    reserve = get_slot(intent_request, "reserve")
    session_attributes = get_session_attributes(intent_request)
    request_attributes = get_request_attributes(intent_request)
    fulfillment_state = "Fulfilled"

    if reserve == "yes":
        # TODO: make post request to /usr/reserve, pass information about user and restaurant information
        pass

    messages = [{
        "contentType": "PlainText",
        "content": "You have finished the journey with dining concierge chatbot. Wish you a good meal!"
    }]

    return close(intent_request, session_attributes, fulfillment_state, messages, request_attributes)
