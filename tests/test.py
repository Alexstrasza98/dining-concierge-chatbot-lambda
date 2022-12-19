from app import lambda_handler
import json
import pprint

if __name__ == "__main__":
    with open("../events/initial_search_success.json") as f:
        event = json.load(f)

    pprint.pprint(lambda_handler(event, None))
