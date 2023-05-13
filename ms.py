from requests import put,get,post
from states import states_order
import json, time

MY_STORAGE_TOKEN = 'fe41eff96185254e5fb3c54d18b183127c594243'

BASE_URL = 'https://online.moysklad.ru/api/remap/1.2/'

HEADERS = {"Authorization": f"Bearer {MY_STORAGE_TOKEN}","Content-Type": "application/json", 'encoding': 'utf-8'}

def _get_metastate(url):
    return get(url,headers=HEADERS).json()['name']

def _get_metaphone(attributes):
    for item in attributes:
        if item['id'] == '327fa9ce-d787-11ed-0a80-01390030e9ad':
            return item['value']
    return '' 

def _get_rent_start(attributes):
    for item in attributes:
        if item['id'] == '66193f95-d788-11ed-0a80-05b500303bff':
            return item['value']
    return ''

def _get_rent_end(attributes):
    for item in attributes:
        if item['id'] == '6619417b-d788-11ed-0a80-05b500303c00':
            return item['value']
    return ''

def _get_metafio(url):
    return get(url,headers=HEADERS).json()['name']

def _get_positions(url):
    res = []
    r = get(url,headers=HEADERS).json()['rows']
    for i in r:
        new_url = i['assortment']['meta']['href']
        res.append(int(get(new_url,headers=HEADERS).json()['code']))
    return res

def get_orders():
    
    limit = 1000
    offset = 0
    url_api = 'entity/customerorder' 
    body = {
        'limit': limit,
        'offset': offset
    }

    response = get(url=f'{BASE_URL}{url_api}',headers=HEADERS, json= body,)
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
        try:
            phone = _get_metaphone(order['attributes'])
        except:
            phone = ''
        fio = str(_get_metafio(order['agent']['meta']['href'])).encode().decode('utf-8')
        try:
            rent_start = _get_rent_start(order['attributes'])
        except:
            continue
        try:
            rent_end = _get_rent_end(order['attributes'])
        except:
            continue
        positions = _get_positions(order['positions']['meta']['href'])
        res.append([id,fio,phone,state,rent_start,rent_end, sum, positions])
    return res

def set_state(id_order, new_state):
    url = f'{BASE_URL}/entity/customerorder/?filter=name={id_order}'
    response = get(url=url, headers=HEADERS)
    if response.status_code == 200:
        order = response.json()['rows'][0]['meta']['href']
    body ={
        'state': {
            'meta': states_order[new_state]['meta']
        }
    }
    r = put(url=order, headers=HEADERS,json=body)
    if r.status_code==200:
        return 'OK'
    else:
        return 'ERROR'

def set_free(id_product, free: bool):
    url = f'{BASE_URL}/entity/product/?filter=code={id_product}'
    response = get(url=url, headers=HEADERS)
    if free:
        value = 'Да'
    else:
        value = 'Нет'
    if response.status_code == 200:
        product = response.json()['rows'][0]['meta']['href']
    body = {
       "attributes":[ 
           {
               "meta": {
                "href": "https://online.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/eb2ea822-e9cf-11ed-0a80-1108005d077a",
                "type": "attributemetadata",
                "mediaType": "application/json"
                },
                # "name": "Свободен",
                'value': value
            }
        ]
    }
    r = put(url=product, headers=HEADERS,json=body)
    if r.status_code == 200:
        return 'OK'
    else:
        return 'ERROR'

def set_product_comment(id_product, comment):
    url = f'{BASE_URL}/entity/product/?filter=code={id_product}'
    response = get(url=url, headers=HEADERS)
    if response.status_code == 200:
        product = response.json()['rows'][0]['meta']['href']
    body = {
       "attributes":[ 
           {
               "meta": {
                    "href": "https://online.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/6f93b889-e9d0-11ed-0a80-00cb005e9834",
                    "type": "attributemetadata",
                    "mediaType": "application/json"
                },
                "name": "Аренды",
                "value": comment
            }
        ]
    }
    r = put(url=product, headers=HEADERS,json=body)
    if r.status_code == 200:
        return 'OK'
    else:
        return 'ERROR'

def set_all_free():
    url = f'{BASE_URL}entity/product'
    body = {
        'offset': 0
    }
    data = []
    response = get(url=url, headers=HEADERS, json=body).json()
    data+=response['rows']
    while len(response['rows']) == 1000:
        body['offset']+=1000
        response = get(url=f'{url}/?offset={body["offset"]}', headers=HEADERS, json=body).json()
        data+=response['rows']
    
    href_list = []
    for line in data:
        href_list.append(line['meta']['href'])
    
    data = []

    for href in href_list:
        data.append({
            "meta": {
                "href": href,
                "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/product/metadata",
                "type": "product",
                "mediaType": "application/json"
            },
            "attributes":[ 
            {
               "meta": {
                "href": "https://online.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/eb2ea822-e9cf-11ed-0a80-1108005d077a",
                "type": "attributemetadata",
                "mediaType": "application/json"
                },
                'value': 'Да'
            }
            ]
        })
    
    url = 'https://online.moysklad.ru/api/remap/1.2/entity/product'
    n = len(data) // 1000
    # print(n)
    for i in range(n):
        r = post(url=url, headers=HEADERS, json=data[1000*i:1000*(i+1)])
    r = post(url=url, headers=HEADERS, json=data[1000*(i+1):])    
    if r.status_code == 200:
        return 'OK'
    else:
        return 'ERROR'

def put_main_data(link):
    r = get(url=link, headers=HEADERS).json()
    id = r['name']
    sum = r['sum']
    state = _get_metastate(r['state']['meta']['href'])
    try:
        phone = _get_metaphone(r['attributes'])
    except:
        phone = ''
    fio = str(_get_metafio(r['agent']['meta']['href'])).encode().decode('utf-8')
    try:
        rent_start = _get_rent_start(r['attributes'])
    except:
        rent_start = ''
    try:
        rent_end = _get_rent_end(r['attributes'])
    except:
        rent_end = ''
    positions = _get_positions(r['positions']['meta']['href'])
    return [id,fio,phone,state,rent_start,rent_end, sum, positions]

def write_active_rents(data: dict):
    set_all_free()
    for product in data.keys():
        lines = data[product]
        text = ''
        for comment in lines:
            start = str(comment['start_datetime'])[:-3]
            end = str(comment['end_datetime'])[:-3]
            fio = comment['FIO']
            phone = comment['phone']
            text+=f'{start} - {end} | {fio} | {phone}\n'
        set_product_comment(product, text)
        set_free(product, False)
        
def leftovers_plus(id_product):
    url = f'{BASE_URL}/entity/product/?filter=code={id_product}'
    response = get(url=url, headers=HEADERS)
    if response.status_code == 200:
        product = response.json()['rows'][0]['meta']['href']
    body = {
        'name': str(time.time())[:-3],
        'organization':{       
            "meta": {
                "href": "https://online.moysklad.ru/api/remap/1.2/entity/organization/924346d3-6543-11eb-0a80-07f1000909a0",
                "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/organization/metadata",
                "type": "organization",
                "mediaType": "application/json",
                "uuidHref": "https://online.moysklad.ru/app/#mycompany/edit?id=924346d3-6543-11eb-0a80-07f1000909a0"
            }
        },
        'store': {
            "meta": {
                "href": "https://online.moysklad.ru/api/remap/1.2/entity/store/92608a7b-6543-11eb-0a80-07f1000909a5",
                "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/store/metadata",
                "type": "store",
                "mediaType": "application/json",
                "uuidHref": "https://online.moysklad.ru/app/#warehouse/edit?id=92608a7b-6543-11eb-0a80-07f1000909a5"
            }
        },
        'positions': [
            {
                'quantity': 1,
                'price': 0,
                'assortment': {
                    "meta": {
                        "href": product,
                        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/product/metadata",
                        "type": "product",
                        "mediaType": "application/json"
                    }
                }
            }
        ]
    }
    url = 'https://online.moysklad.ru/api/remap/1.2/entity/enter'
    r = post(url = url, headers=HEADERS, json=body)
    if r.status_code == 200:
        return 'OK'
    else:
        return 'ERROR'

if __name__ == '__main__':
    ...