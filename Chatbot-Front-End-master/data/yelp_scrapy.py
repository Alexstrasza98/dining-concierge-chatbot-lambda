import requests
import json
import sys

API_KEY = '6-dnnwPsU_ZD3n5riURfLONj1TaVix1VkiDbqal4bxiT19jaogqMinVBUkFHhEJ16Gh3DxNxfuqxCHLeSr838SU8Um-4UcQnIfZB-heGn3G7_d5OqvELsj8Y1ZdJXnYx'
# cuisines = ['chinese', 'japanese', 'italian', 'korean', 'french', 'american', 'mexican', 'indian']
cuisines = ['japanese','chinese']

def detail(api_key, id):
    url = 'https://api.yelp.com/v3/businesses/' + id
    headers = {'Authorization': 'Bearer %s' % api_key}
    req = requests.get(url, headers = headers)
    return req.json()
    

def request(api_key, terms, location = "NY", limit = 50):
    url = 'https://api.yelp.com/v3/businesses/search'
    headers = {'Authorization': 'Bearer %s' % api_key}
    response = []
    id_set = set()
    for term in terms:  
        offset = 0   
        #TODO: change to 20
        for i in range(20):
            offset += 50
            params = {'term':term,'location': location, 'limit': limit, 'offset': offset}
            req = requests.get(url, params = params, headers = headers)
            parsed = req.json()
            try:
                businesses = parsed["businesses"]
                
                for business in businesses:
                    dct = {}
                    id = business['id']
                    if id not in id_set:
                        dct['id'] = id
                        dct['name'] = business['name'] 
                        dct['category'] = term    # cuisine type
                        dct['rating'] = business['rating'] if business['rating'] != '' else 0
                        dct['review_count'] = business['review_count'] if business['review_count'] != '' else 0
                        dct['coordinates'] = business['coordinates'] if business['coordinates'] != '' else 'None'
                        dct['address'] = ", ".join(business['location']['display_address']) if business['location']['display_address'] != '' else 'None'
                        dct['phone'] = business["display_phone"] if business["display_phone"] != '' else 'None'
                        dct['zip_code'] = business['location']['zip_code'] if business['location']['zip_code'] != '' else 'None'

                        details = detail(api_key, id)
                        dct['hours'] = details['hours'][0]['open'] if details['hours'][0]['open'] != '' else 'None'

                        response.append(dct)
                        id_set.add(id)
            except:
                continue
    
    print(len(response))
    with open('data.json', 'w') as openfile:
        json.dump(response, openfile, indent = 4)
    
# fields: id, name, review_count, category (new) , display_phone, 
# display_address (join list), rating, price, open hours, coordinates, zip code
def main():         
    request(API_KEY, cuisines)


if __name__ == '__main__':
    main()
