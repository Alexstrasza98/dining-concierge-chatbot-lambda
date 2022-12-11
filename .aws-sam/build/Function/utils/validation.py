import dateutil.parser
import math
import datetime


# Helper validation function
def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


# Main validation function
def validate_dining_suggestion(location, cuisine, time, date, numberOfPeople, phoneNumber):
    locations = ['manhattan', 'new york']
    if location is not None and location.lower() not in locations:
        return build_validation_result(False,
                                       'Location',
                                       'We do not have suggestions for {}, would you like suggestions for a differenet location?  '
                                       'Our most popular location is Manhattan '.format(location))

    cuisines = ['chinese', 'indian', 'italian', 'japanese', 'mexican', 'thai', 'korean', 'arab', 'american']
    if cuisine is not None and cuisine.lower() not in cuisines:
        return build_validation_result(False,
                                       'Cuisine',
                                       'We do not have suggestions for {}, would you like suggestions for a differenet cuisine ?  '
                                       'Our most popular Cuisine is Indian '.format(cuisine))
    if date is not None:
        if not isvalid_date(date):
            return build_validation_result(False, 'Date',
                                           'I did not understand that, what date would you like to have the recommendation for?')
        elif datetime.datetime.strptime(date, '%Y-%m-%d').date() < datetime.date.today():
            return build_validation_result(False, 'Date',
                                           'Sorry, that is not possible What day would you like to have the recommendation for?')

    if time is not None:
        if len(time) != 5:
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'DiningTime', None)

        hour, minute = time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'Time', None)

        if hour < 10 or hour > 24:
            # Outside of business hours
            return build_validation_result(False, 'Time',
                                           'Our business hours are from 10 AM. to 11 PM. Can you specify a time during this range?')

    if numberOfPeople is not None and not numberOfPeople.isnumeric():
        return build_validation_result(False,
                                       'NumberOfPeople',
                                       'That does not look like a valid number {}, '
                                       'Could you please repeat?'.format(numberOfPeople))

    if phoneNumber is not None and not phoneNumber.isnumeric():
        return build_validation_result(False,
                                       'PhoneNumber',
                                       'That does not look like a valid number {}, '
                                       'Could you please repeat? '.format(phoneNumber))
    return build_validation_result(True, None, None)


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }