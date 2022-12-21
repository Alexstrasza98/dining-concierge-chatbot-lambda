import json
import requests
import time


cuisines = ['chinese', 'japanese', 'italian', 'korean', 'french', 'american', 'mexican', 'indian']
# API_KEY = '6-dnnwPsU_ZD3n5riURfLONj1TaVix1VkiDbqal4bxiT19jaogqMinVBUkFHhEJ16Gh3DxNxfuqxCHLeSr838SU8Um-4UcQnIfZB-heGn3G7_d5OqvELsj8Y1ZdJXnYx'
# API_KEY = "ueSaG54dzEo5zQeM8aI2LT5C4krMvCYm5HJiNWuh13viiwEgh-Zl3qk3Te1ZOfYK6l4kWDIQzaL4O0sezTPUejlxXv_4-v0DDcguHQjazqPClbvOhTclNpJXOe6YXXYx"
# API_KEY = "SfzJ47_GxNUEXg4qO2Xk4rnjFTsCPFJZ7YMhHcdZr3VSxW7wSYS_1-hE6zBCbGluBNiU3XTmDnXsyVWFCPCHd3sl64MkJb7Z0QZbnl4ShdNtqBA9HLK_OmPDn3hRXnYx"
API_KEY = "Vv3D0MWqERhHbN7M5C1Wb1tTvsezZeISd8u6T50QI7zxkdzaLXhjQjCdRhiTqR7w1BZtPc722pRAaawBoKjgayUauLDxTV9lzfL12pwUzFVoUmAC-HUZ9s5fc_iCXHYxç"
headers = {'Authorization': 'Bearer %s' % API_KEY}
root = 'https://api.yelp.com/v3/businesses/'
id_set = set()

def detail(id, cnt):
    url = root + id
    req = requests.get(url, headers = headers)
    if cnt % 100 == 0:
        print(req.status_code)
    return req.json()
    
def adapt(cuisine):
    
    response = []
    cnt = 0

    filename = cuisine + '.json'
    with open(filename, 'r') as f:
        data = json.load(f)

    for key, val in data.items():
        if 'businesses' not in val: continue

        businesses = val["businesses"]
        for business in businesses:
            dct = {}
            id = business['id']
            if id not in id_set:
                dct['id'] = id
                dct['name'] = business['name'] 
                dct['category'] = cuisine    # cuisine type
                dct['rating'] = business['rating'] if 'rating' in business and business['rating'] != '' else 0
                dct['review_count'] = business['review_count'] if 'review_count' in business and business['review_count'] != '' else 0
                dct['coordinates'] = business['coordinates'] if 'coordinates' in business and business['coordinates'] != '' else 'None'
                dct['address'] = ", ".join(business['location']['display_address']) if 'location' in business and 'display_address' in business['location'] and business['location']['display_address'] != '' else 'None'
                dct['phone'] = business["display_phone"] if 'display_phone' in business and business["display_phone"] != '' else 'None'
                dct['zip_code'] = business['location']['zip_code'] if 'location' in business and 'zip_code' in business['location'] and business['location']['zip_code'] != '' else 'None'

                details = detail(id, cnt)
                dct['hours'] = details['hours'][0]['open'] if 'hours' in details and details['hours'][0]['open'] != '' else 'None'

                response.append(dct)
                id_set.add(id)
                cnt += 1
            if cnt == 800:
                break
    print(cnt)
    
    newfile = cuisine + '0.json'
    with open(newfile, 'w') as f:
        json.dump(response, f, indent = 4)
       

def main():  
    for cuisine in cuisines:    
        adapt(cuisine)
        time.sleep(150)

if __name__ == '__main__':
    main()
