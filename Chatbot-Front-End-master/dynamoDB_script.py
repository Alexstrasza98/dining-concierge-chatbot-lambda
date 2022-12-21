#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import boto3
import time
'''
Data format for restaurant json
{
    "id": "p4W_z-zh96LHEAtQ8LRSVQ",
    "name": "Shinagawa",
    "category": "japanese",
    "rating": 4.5,
    "review_count": 112,
    "coordinates": {
        "latitude": 40.74549,
        "longitude": -73.97935
    },
    "address": "157 E 33rd St, New York, NY 10016",
    "phone": "(917) 261-6635",
    "zip_code": "10016",
    "hours": [
        {
            "is_overnight": false,
            "start": "1100",
            "end": "2230",
            "day": 0
        },
        ... to "day": 5
    ]
},
'''
STRING_TYPES = ["id", "name", "category", "address", "phone", "zip_code"]
NUMBERS_TYPES = ["rating", "review_count"]
TABLE_NAME = "yelp-restaurants"
BATCH_SIZE = 25


def addDataTypes(rstr):
    '''Add dynamoDB types for each attribute'''
    def _pack(key, value, Type):
        '''Attribute in dynamoDB: {key: {dataType: value}}'''
        if not value:
            print(key, value, Type)
        return (key, {Type: value})
    #print(rstr)
    nrstr = list()
    for key in STRING_TYPES:
        nrstr += _pack(key, rstr[key], "S"),
    for key in NUMBERS_TYPES:
        nrstr += _pack(key, str(rstr[key]), "N"),

    for key in ["latitude", "longitude"]:
        nrstr += _pack(key, str(rstr["coordinates"][key]), "N"),

    if rstr["hours"] and rstr["hours"] != 'None':
        openDays = list()
        for day in rstr["hours"]:
            dayOpenHour = dict([_pack(key, str(day[key]), "S") for key in ["day", "start", "end"]])
            openDays += {"M": dayOpenHour},
        nrstr += _pack("open_days", openDays, "L"),
    else:
        nrstr += _pack("open_days", "None", "S"),

    return dict(nrstr)


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


def pack(restaurants):
    '''Convert json of restaurants to dynamoDB Insert Request Format'''
    requests = list()
    for rstr in restaurants:
        nrstr = addDataTypes(rstr)
        request = {"PutRequest": {"Item": nrstr}}
        requests.append(request)

    return requests


def uploadData(requests):
    client = boto3.client('dynamodb')
    idx = 0
    while idx < len(requests):
        request_batch = requests[idx:idx+BATCH_SIZE]
        idx += BATCH_SIZE
        data = {TABLE_NAME: request_batch}
        response = client.batch_write_item(RequestItems=data)
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            print("HTTPError with Status Code {}".format(response['ResponseMetadata']['HTTPStatusCode']))
            exit(-1)
    time.sleep(1)


def pullData(id):
    """Pull a row of a restaurant(dict) by its id. Return None if not such restaurant"""
    client = boto3.client('dynamodb')
    response = client.get_item(TableName=TABLE_NAME, Key={'id':{'S': id}})
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        print("HTTPError with Status Code {}".format(response['ResponseMetadata']['HTTPStatusCode']))
        exit(-1)

    return removeDataTypes(response['Item'])

def writeToFile(restaurants, filename):
    with open(filename, "w") as f:
        f.write(json.dumps(restaurants, indent=4))

def uploadAll(dir_path):
    'Upload all data under dir_path to dynamoDB'
    for _, _, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(dir_path, file)
            _, extension = os.path.splitext(file_path)
            if extension == '.json':
                print("Uploading file {} to dynamoDB".format(file_path))
                try:
                    with open(file_path, 'r') as f:
                        restaurants = json.load(f)
                except:
                    print(file_path)
                    raise
                #writeToFile(pack(restaurants), 'tmp.json')
                uploadData(pack(restaurants))
                print("File {} is uploaded successfully".format(file_path))
    

if __name__ == '__main__':
    uploadAll('data')
    #print(pullData('1xA_G41I-OVyZGXARY71UQ'))