"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages orders for flowers.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'OrderFlowers' template.
For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""
import time
import os
import logging
from utils.intents import initial_search_yelp, welcome

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def dispatch(intent_request, context):
    """
    Called when the user specifies an intent for this bot.
    """

    # logger.debug(
    #     'dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request["sessionState"]["intent"]["name"]

    # Dispatch to your chatbot intent handlers
    if intent_name == 'SearchRestuarants':
        return initial_search_yelp(intent_request, context)
    elif intent_name == 'Welcome':
        return welcome(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    # logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event, context)


