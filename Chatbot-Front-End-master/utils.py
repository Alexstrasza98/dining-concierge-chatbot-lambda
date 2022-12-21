import boto3
import json
import requests
from requests_aws4auth import AWS4Auth

URL = 'https://search-restaurants-rnueuwllhgewuy3zxqid2q775y.us-east-1.es.amazonaws.com/restaurants/{}'
TABLE_NAME = "yelp-restaurants"


def removeDataTypes(rstr):
    def ravel_map(m):
        assert isinstance(m, dict), "Argument should be a mapping {dtype: value}"
        dtype, value = [*m.items()][0]
        if dtype == "S":
            return value
        elif dtype == "N":
            return float(value)
        elif dtype in "LM":
            return removeDataTypes(value)
        else:
            raise Exception("Error: unexpected data type {}".format(dtype))
    if isinstance(rstr, dict):
        mapping = {}
        for key, value in rstr.items():
            mapping[key] = ravel_map(value)
        return mapping
    elif isinstance(rstr, list):
        return [ravel_map(m) for m in rstr]

    return None

def get_restaurant_from_dynamoDB(id):
    """Pull a row of a restaurant(dict) by its id. Return None if not such restaurant"""
    client = boto3.client('dynamodb')
    response = client.get_item(TableName=TABLE_NAME, Key={'id':{'S': id}})
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        print("HTTPError with Status Code {}".format(response['ResponseMetadata']['HTTPStatusCode']))
        exit(-1)

    return removeDataTypes(response['Item'])

def send_signed(method, url, service='es', region='us-east-1', body=None):
    credentials = boto3.Session().get_credentials()
    auth = AWS4Auth(credentials.access_key, credentials.secret_key, 
                  region, service, session_token=credentials.token)

    fn = getattr(requests, method)
    if body and not body.endswith("\n"):
        body += "\n"
    try:
        response = fn(url, auth=auth, data=body, 
                        headers={"Content-Type":"application/json"})
        if response.status_code != 200:
            raise Exception("{} failed with status code {}".format(method.upper(), response.status_code))
        return response.content
    except Exception:
        raise

def es_search(criteria):
    url = URL.format('_search')
    return send_signed('get', url, body=json.dumps(criteria))

def get_restaurants_from_es(category):
    """Given a category, return a list of restaurant ids in that category"""
    criteria = {
        "query": { "match": {'category': category} },
    }
    content = es_search(criteria)
    content = json.loads(content)
    return [rstr['_source']['id'] for rstr in content['hits']['hits']]

