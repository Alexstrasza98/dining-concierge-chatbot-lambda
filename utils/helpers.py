def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']


def get_slot(intent_request, slot_name):
    slots = get_slots(intent_request)
    if slots is not None and slot_name in slots and slots[slot_name] is not None:
        return slots[slot_name]['value']['interpretedValue']
    else:
        return None


def get_session_attributes(intent_request):
    session_state = intent_request['sessionState']
    if 'sessionAttributes' in session_state:
        return session_state['sessionAttributes']

    return {}


def get_request_attributes(intent_request):
    if 'sessionAttributes' in intent_request:
        return intent_request['requestAttributes']

    return {}


def mile_to_meter(mile):
    return int(min(mile * 1609, 40000))


def price_to_dollar(price):
    if price < 20:
        return 1
    elif price < 50:
        return 2
    elif price < 120:
        return [2, 3]
    return [3, 4]
