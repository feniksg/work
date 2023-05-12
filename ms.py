from requests import put,get,post
import json

MY_STORAGE_TOKEN = 'fe41eff96185254e5fb3c54d18b183127c594243'

BASE_URL = 'https://online.moysklad.ru/api/remap/1.2/'

HEADERS = {"Authorization": f"Bearer {MY_STORAGE_TOKEN}","Content-Type": "application/json"}

def _get_metastate(url):
    return get(url,headers=HEADERS).json()['name']

def _get_metaphone(attributes):
    for item in attributes:
        if item['id'] == '327fa9ce-d787-11ed-0a80-01390030e9ad':
            return item['value']
    return '' 

def get_orders():
    
    limit = 1000
    offset = 0
    url_api = 'entity/customerorder' 
    body = {
        'limit': limit,
        'offset': offset
    }

    response = get(url=f'{BASE_URL}{url_api}',headers=HEADERS, json= body)
    if response.status_code == 200:
        data = response.json()['rows']
    else:
        return "ERROR: Couldn't get order list"
    r = data
    while len(r) == limit:
        offset+=1000
        r = get(url=f'{BASE_URL}{url_api}',headers=HEADERS, json= body).json()['rows']
        data+=r
    res = []
    for order in data:
        id = order['name']
        sum = order['sum']
        state = _get_metastate(order['state']['meta']['href'])
        phone = _get_metaphone(order['attributes'])

    # with open('output.json', 'w+') as f:
        # json.dump(data, f, indent=2)
    


if __name__ == '__main__':
    pass
    
