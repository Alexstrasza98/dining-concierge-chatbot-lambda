# To elicit another intent
def elicit_intent(intent_request, session_attributes, fulfillment_state, message):
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'ElicitIntent',
                'intentName': 'ViewSpecificRestaurant',
                'slotToElicit': 'businessID'
            },
        },
        'messages': [message] if message is not None else None,
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }


# To elicit another slot
def elicit_slot(session_attributes, intent, slot_to_elicit, messages, request_attributes, session_id):
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'ElicitSlot',
                'slotToElicit': slot_to_elicit,
            },
            'intent': intent
        },
        'messages': messages,
        'sessionId': session_id,
        'requestAttributes': request_attributes
    }


# Close the conversation
def close(intent_request, session_attributes, fulfillment_state, messages, request_attributes):

    intent_request['sessionState']['intent']['state'] = fulfillment_state
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': messages,
        'sessionId': intent_request['sessionId'],
        'requestAttributes': request_attributes
    }


