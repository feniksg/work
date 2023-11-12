from requests import put,get,post
from states import states_order
from settings import MY_STORAGE_TOKEN
import json, time, logging

logging.basicConfig(level=logging.INFO, filename="ms_log.log",filemode="a")

STATES = {
    'Бронь': 'Booked',
    'Отмена': 'Cancel',
    'Аренда': 'InRent',
    'Задерживается': 'Overdue',
    'Закрыта': 'Closed',
    '[N] Принят, ожидается оплата': 'OkWait',
    '[N] Принят, оплачен': 'OkPayment',
    'Прохождение химчистки': 'Closed',
    'Продажа': 'Sold',
    'Сохранение брони': 'KeepBooking'
}

BASE_URL = 'https://online.moysklad.ru/api/remap/1.2/'

HEADERS = {"Authorization": f"Bearer {MY_STORAGE_TOKEN}","Content-Type": "application/json", 'encoding': 'utf-8'}

#Получение метаданных статуса заказ
def _get_metastate(url: str) -> dict:
    return STATES[get(url,headers=HEADERS).json()['name']]

#Получение номера телефона клиента
def _get_metaphone(attributes) -> str:
    for item in attributes:
        if item['id'] == '327fa9ce-d787-11ed-0a80-01390030e9ad':
            return item['value']
    return '' 

#Получение даты начала аренды
def _get_rent_start(attributes):
    for item in attributes:
        if item['id'] == '66193f95-d788-11ed-0a80-05b500303bff':
            return item['value']
    return ''

#Получение даты конца аренды
def _get_rent_end(attributes):
    for item in attributes:
        if item['id'] == '6619417b-d788-11ed-0a80-05b500303c00':
            return item['value']
    return ''

#Получение ФИО
def _get_metafio(url):
    return get(url,headers=HEADERS).json()['name']

#Получение Товаров в аренде
def _get_positions(url):
    res = []
    r = get(url,headers=HEADERS).json()['rows']
    for i in r:
        new_url = i['assortment']['meta']['href']
        res.append(int(get(new_url,headers=HEADERS).json()['code']))
    return res

#Получение метаданных контрагента
def _get_agent_meta(url):
    return get(url,headers=HEADERS).json()['agent']['meta']['href']

#Создание входящего платежа
def create_inpayment(id_order: int, amount: int):
    url = f'{BASE_URL}entity/customerorder/?filter=name={id_order}'
    response = get(url=url, headers=HEADERS)
    if response.status_code == 200 and response.json()['rows'] != []:
        order = response.json()['rows'][0]['meta']['href']
    else:
        return None
    agent = _get_agent_meta(order)
    data ={
        "operations": [
            {
                "meta": {
                    "href": order,
                    "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/metadata",
                    "type": "customerorder",
                    "mediaType": "application/json"
                }
            }
        ],
    }
    url = 'https://online.moysklad.ru/api/remap/1.2/entity/paymentin/new'
    data = put(url=url, headers=HEADERS, json=data).json()
    data['operations'][0]['linkedSum'] = amount
    data['sum'] = amount
    url = 'https://online.moysklad.ru/api/remap/1.2/entity/paymentin'
    response = post(url=url, headers=HEADERS, json=data)
    return 'ok'

#Получение всех аренд и продаж
def get_orders():
    
    limit = 1000
    offset = 0
    url_api = 'entity/customerorder' 
    
    response = get(url=f'{BASE_URL}{url_api}?limit={limit}&offset={offset}',headers=HEADERS)
    if response.status_code == 200:
        data = response.json()['rows']
    else:
        return "ERROR: Couldn't get order list"
    r = data
    while len(r) == limit:
        offset+=1000
        r = get(url=f'{BASE_URL}{url_api}?limit={limit}&offset={offset}',headers=HEADERS).json()['rows']
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

        rent_start = _get_rent_start(order['attributes'])
        rent_end = _get_rent_end(order['attributes'])

        if not rent_start and not rent_end:
            continue

        positions = _get_positions(order['positions']['meta']['href'])
        res.append([id,fio,phone,state,rent_start,rent_end, sum, positions])
    return res

#Получение ссылки для платежа
def get_link_from_payment(link: str) -> str: 
    responce = get(url=link, headers=HEADERS)
    if responce.status_code == 200:
        return responce.json()['operations'][0]['meta']['href']
    else:
        return None
#Преобразует номер из формата 00001 в 1
def normalize_number(link):
    response = get(url=link, headers=HEADERS)
    if response.status_code == 200:
        name = response.json()['name']
        name = int(name)
        data = {
            "name": name
        }
        response = put(url=link, headers=HEADERS, json=data)
        
#Установить статус заказа
def set_state(id_order, new_state):
    url = f'{BASE_URL}entity/customerorder/?filter=name={id_order}'
    response = get(url=url, headers=HEADERS)
    if response.status_code == 200:
        if response.json()['rows'] != []:
            order = response.json()['rows'][0]['meta']['href']
        else:
            logging.error(f'set_state: Order not found. Order id - [{id_order}]')
            return 'ERROR'
    else:
        logging.error(f'set_state: Responce (get order) status code - [{response.status_code}].')
        return 'ERROR'
    body ={
        'state': {
            'meta': states_order[new_state]['meta']
        }
    }
    r = put(url=order, headers=HEADERS,json=body)
    if r.status_code==200:
        return 'OK'
    else:
        logging.error(f'set_state: Responce (change state) status code - [{response.status_code}].')
        return 'ERROR'

#Установить свободен ли товар
def set_free(id_product, free: bool):
    url = f'{BASE_URL}entity/product/?filter=code={id_product}'
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

#Вписать активные аренды поле товара
def set_product_comment(id_product, comment):
    url = f'{BASE_URL}entity/product/?filter=code={id_product}'
    response = get(url=url, headers=HEADERS)
    if response.status_code == 200:
        product = response.json()['rows'][0]['meta']['href']
    else:
        return 'ERROR'
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

#Установить себестоимость для товара
def set_selfprice(link):
    try:
        value = get(url=link, headers=HEADERS).json()['buyPrice']['value']
    except:
        value = 0
    body = {
        "attributes": [
            {
                "meta": {
                    "href": "https://online.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/3edab5e5-06cc-11ee-0a80-08d500177993",
                    "type": "attributemetadata",
                    "mediaType": "application/json"
                    },
                "id": "3edab5e5-06cc-11ee-0a80-08d500177993",
                "name": "Себестоимость",
                "type": "double",
                "value": value / 100
            }
        ]
    }
    r = put(url=link, headers=HEADERS,json=body)
    if r.status_code == 200:
        return "OK"
    else:
        return "Something wrong"

#Установить всем товарам статус свободедн
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
            },
            {
               "meta": {
                    "href": "https://online.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/6f93b889-e9d0-11ed-0a80-00cb005e9834",
                    "type": "attributemetadata",
                    "mediaType": "application/json"
                },
                "name": "Аренды",
                "value": ''
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

#Получить по ссылке основные данные заказа
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
    if rent_start and rent_end:
        return [[id,fio,phone,state,rent_start,rent_end, sum, positions]]
    else:
        return None

#Установить активные аренды для всех товаров
def write_active_rents(data: dict):
    set_all_free()
    for product in data.keys():
        lines = data[product]
        text = ''
        for comment in lines:
            start = str(comment['start_datetime'])[:-3]
            end = str(comment['end_datetime'])[:-3]
            fio = comment['fio_rent']
            phone = comment['phone_rent']
            text+=f'{start} - {end} | {fio} | {phone}\n'
        set_product_comment(product, text)
        set_free(product, False)

#Увеличить количество товара в остатках        
def leftovers_plus(id_product):
    url = f'{BASE_URL}entity/product/?filter=code={id_product}'
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

#Получить артикул товара
def _get_article(product_id):
    url = f'https://online.moysklad.ru/api/remap/1.2/entity/product/?filter=code={product_id}'
    article = get(url, headers=HEADERS).json()['rows'][0]['article']
    return article

#Получить список артикулов в заказе
def get_articles_from_order(order_id):
    result = []
    url = f'https://online.moysklad.ru/api/remap/1.2/entity/customerorder/?filter=name={order_id}'
    r = get(url, headers=HEADERS).json()['rows'][0]['meta']['href']
    positions = put_main_data(r)[0][-1]
    for pos in positions:
        result.append(_get_article(pos))
    return result

#записать артикулы товаров в поле заказа
def set_articles_order(link):
    positions_url = get(url=link, headers=HEADERS).json()['positions']['meta']['href']
    rows = get(url=positions_url, headers=HEADERS).json()['rows']
    articles = []
    for row in rows:
        product_url = row['assortment']['meta']['href']
        try:
            article = get(url=product_url, headers=HEADERS).json()['article']
            articles.append(article)
        except:
            ...
    output = ', '.join(articles)
    data = {
        "attributes":[
            {"meta": {
                "href": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/metadata/attributes/e47e0fdf-4789-11ee-0a80-08db00172a76",
                "type": "attributemetadata",
                "mediaType": "application/json"
            },
            "value": output
            }
        ]
    }
    r = put(url = link, headers=HEADERS, json=data)
    if r.status_code == 200:
        return "OK", r.status_code
    else:
        return "Something wrong", r.status_code
    
#Установить себестоимость для всего заказа
def set_selfprice_order(link):
    positions_url = get(url=link, headers=HEADERS).json()['positions']['meta']['href']
    rows = get(url=positions_url, headers=HEADERS).json()['rows']
    selfprice = 0
    for row in rows:
        product_url = row['assortment']['meta']['href']
        try:
            buyprice = get(url=product_url, headers=HEADERS).json()['buyPrice']['value']
        except:
            buyprice = 0
        selfprice+=buyprice
    data = {
        "attributes":[
            {"meta": {
                "href": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/metadata/attributes/9aa0e4d5-06dc-11ee-0a80-04860027416b",
                "type": "attributemetadata",
                "mediaType": "application/json"
            },
            "value": float(selfprice / 100)
            }
        ]
    }
    r = put(url = link, headers=HEADERS, json=data)
    if r.status_code == 200:
        return "OK", r.status_code
    else:
        return "Something wrong", r.status_code

#Получение поля доп. расходы для товара по ссылке
def get_additional_expenses(link):
    response = get(link, headers=HEADERS).json()
    attrs = response['attributes']
    expenses = 0
    for attribute in attrs:
        if attribute['id'] == '95621bc6-085a-11ee-0a80-0c7300357cc4':
            expenses = attribute['value']
    return expenses

#Получение суммы доп. расходов для заказа
def get_sum_additional_expenses(link):
    expenses_sum = 0
    positions_url = get(link, headers=HEADERS).json()['positions']['meta']['href']
    products = get(positions_url, headers=HEADERS).json()['rows']
    for product in products:
        expenses_sum+=get_additional_expenses(product['assortment']['meta']['href'])
    return expenses_sum

#Установить рентабельность для заказа
def set_rentable(link):
    order = get(url=link, headers=HEADERS).json()
    state = _get_metastate(order['state']['meta']['href'])
    suma = order['sum'] / 100
    attributes = order['attributes']
    self_price = 0
    for attr in attributes:
        if attr['id'] == '9aa0e4d5-06dc-11ee-0a80-04860027416b':
            self_price = attr['value']
    if state == 'Sold':
        prib = suma - self_price
        rent = prib * 100 / prib
    else:
        expenses_sum = get_sum_additional_expenses(link)
        clear_sum = suma - expenses_sum
        rent = clear_sum / suma * 100
        prib = clear_sum
    data = {
            "attributes" : [
                {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/metadata/attributes/cab054bc-085a-11ee-0a80-10980036abdd",
                        "type": "attributemetadata",
                        "mediaType": "application/json"
                    },
                    "value": prib
                },
                {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/metadata/attributes/cab05654-085a-11ee-0a80-10980036abde",
                        "type": "attributemetadata",
                        "mediaType": "application/json"
                    },
                    'value': f'{rent}%'
                }
            ]
        }
    response = put(url=link, headers=HEADERS, json=data)
    if response.status_code == 200:
        return "OK"
    else:
        return "Something wrong"

#Инициировать обновление всех товаров (Работает около 10-15 минут на 2,5к товаров)
def init_all_product_update():
    tojson = {
        'attributes':[
            {
                "meta": {
                    "href": "https://online.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/5488026b-0861-11ee-0a80-0486003855c5",
                    "type": "attributemetadata",
                    "mediaType": "application/json"
                },
                'value': int(round(time.time()))
            }
        ]
    }
    limit = 500
    offset = 0
    url_api = 'entity/product' 
    body = {
        'limit': limit,
        'offset': offset
    }
    response = get(url=f'{BASE_URL}{url_api}/?limit={limit}&offset={offset}',headers=HEADERS, json= body,)
    if response.status_code == 200:
        data = response.json()['rows']
    else:
        return "ERROR: Couldn't get product list"
    r = data
    while len(r) == limit:
        offset+=500
        r = get(url=f'{BASE_URL}{url_api}/?limit={limit}&offset={offset}',headers=HEADERS, json= body).json()['rows']
        data+=r
    links = []
    for item in data:
        links.append(item['meta']['href'])
    with open('productslinks.json', 'w+') as f:
        json.dump(links, f, indent=2)
    for link in links:
        put(link, headers=HEADERS, json= tojson)
        time.sleep(0.2)

def init_all_order_update():
    tojson = {
        'attributes':[
            {
                "meta": {
                    "href": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/metadata/attributes/78e3d009-0868-11ee-0a80-07c2003659a8",
                    "type": "attributemetadata",
                    "mediaType": "application/json"
                },
                'value': int(round(time.time()))
            }
        ]
    }
    limit = 500
    offset = 0
    url_api = 'entity/customerorder' 
    body = {
        'limit': limit,
        'offset': offset
    }
    response = get(url=f'{BASE_URL}{url_api}/?limit={limit}&offset={offset}',headers=HEADERS, json= body,)
    if response.status_code == 200:
        data = response.json()['rows']
    else:
        return "ERROR: Couldn't get order list"
    r = data
    while len(r) == limit:
        offset+=500
        r = get(url=f'{BASE_URL}{url_api}/?limit={limit}&offset={offset}',headers=HEADERS, json= body).json()['rows']
        data+=r
    links = []
    for item in data:
        links.append(item['meta']['href'])
    with open('orderlinks.json', 'w+') as f:
        json.dump(links, f, indent=2)
    for link in links:
        put(link, headers=HEADERS, json= tojson)
        time.sleep(0.2)

#Получить метаданные администратора
def _get_personal_meta(name):
    url = f'https://online.moysklad.ru/api/remap/1.2/entity/customentity/c62355f1-006a-11ee-0a80-06df000b2730/?filter=name={name}'
    responce = get(url, headers=HEADERS).json()['rows'][0]['meta']
    name = get(responce['href'], headers=HEADERS).json()['name']
    data = {'meta':responce, 'name': name}
    print(data)
    return data

#Создание товара
def create_item(item: dict):
    url = f'{BASE_URL}entity/product'
    name = item['name']
    externalCode = item['externalCode']
    code = item['externalCode']
    article = item['article']
    try:
        salePrice = int(item['salePrice'])
    except:
        salePrice = item['salePrice']
    if type(salePrice) != int or salePrice == None or salePrice == '':
        salePrice = 0
    try:
        photoPrice = int(item['photoPrice'])
    except:
        photoPrice = item['photoPrice']
    if type(photoPrice) != int or photoPrice == None or photoPrice == '':
        photoPrice = 0
    try:
        partyPrice = int(item['partyPrice'])
    except:
        partyPrice = item['photoPrice']
    if type(partyPrice) != int or partyPrice == None or partyPrice == '':
        partyPrice = 0
    try:
        oldPrice = int(item['oldPrice'])
    except:
        oldPrice = item['oldPrice']
    if type(oldPrice) != int or oldPrice == None or oldPrice == '':
        oldPrice = 0
    
    body = {
        "name" : name,
        "externalCode" : externalCode,
        "code": code,
        "article" : article,
        "salePrices": [
            {
                "priceType": {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/context/companysettings/pricetype/92624147-6543-11eb-0a80-07f1000909ab",
                        "type": "pricetype",
                        "mediaType": "application/json"
                    }
                },
                "value" : salePrice*100,
                "currency": {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/entity/currency/9260d73b-6543-11eb-0a80-07f1000909aa",
                        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/currency/metadata",
                        "type": "currency",
                        "mediaType": "application/json",
                    }
                }
            },
            {
                "priceType": {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/context/companysettings/pricetype/df4af656-d499-11ed-0a80-0df40029a0da",
                        "type": "pricetype",
                        "mediaType": "application/json"
                    }
                },
                "value" : photoPrice*100,
                "currency": {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/entity/currency/9260d73b-6543-11eb-0a80-07f1000909aa",
                        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/currency/metadata",
                        "type": "currency",
                        "mediaType": "application/json"
                    }
                }
            },
            {
                "priceType": {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/context/companysettings/pricetype/df4af77b-d499-11ed-0a80-0df40029a0db",
                        "type": "pricetype",
                        "mediaType": "application/json"
                    }
                },
                "value" : partyPrice*100,
                "currency": {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/entity/currency/9260d73b-6543-11eb-0a80-07f1000909aa",
                        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/currency/metadata",
                        "type": "currency",
                        "mediaType": "application/json",
                    }
                }
            },
            {
                "priceType": {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/context/companysettings/pricetype/10bfe5e0-b927-11ed-0a80-0d23003adcb4",
                        "type": "pricetype",
                        "mediaType": "application/json"
                    }
                },
                "value" : oldPrice*100,
                "currency": {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/entity/currency/9260d73b-6543-11eb-0a80-07f1000909aa",
                        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/currency/metadata",
                        "type": "currency",
                        "mediaType": "application/json",
                    }
                }
            }
        ],
        "productFolder": {
                "meta":{
                    "href": "https://online.moysklad.ru/api/remap/1.2/entity/productfolder/583f7744-d1df-11ed-0a80-0053005e66e5",
                    "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/productfolder/metadata",
                    "type": "productfolder",
                    "mediaType": "application/json"
                }
        }
    }
    
    r = post(url=url, headers=HEADERS, json=body)
    if r.status_code == 200:
        print(f'[{code}] Успешно экпортирован')
        logging.info(f'[Update Item] Statuc Code: {r.status_code} {body["code"]}|{body["article"]}|{body["name"]}')
    elif r.status_code == 400:
        print(f'[{code}] Произошла ошибка, проверьте поля ')
        logging.error(f'[Update Item] Statuc Code: {r.status_code} {body["code"]}|{body["article"]}|{body["name"]}')
    elif r.status_code == 412:
        print(f'[{code}] Произошла ошибка, товар с таким кодом уже существует. Возможно он в архиве.')
        logging.error(f'[Update Item] Statuc Code: {r.status_code} {body["code"]}|{body["article"]}|{body["name"]}')
    else:
        print(f'[{code}] Произошла ошибка, и я не знаю какая...')
        logging.error(f'[Update Item] Statuc Code: {r.status_code} {body["code"]}|{body["article"]}|{body["name"]}')

#Проверка наличия товара    
def check_item(code):
    url = f'{BASE_URL}entity/product/?filter=code={code}'
    r = get(url= url, headers = HEADERS)
    if r.json()["rows"] != []:
        return True
    else:
        return False

#Обновление товара
def update_item(item: dict):
    name = item['name']
    externalCode = item['externalCode']
    code = item['externalCode']
    url = f'https://online.moysklad.ru/api/remap/1.2/entity/product/?filter=code={code}'
    objectId = get(url = url, headers=HEADERS).json()['rows'][0]['id']
    url = f'https://online.moysklad.ru/api/remap/1.2/entity/product/{objectId}'
    article = item['article']
    try:
        salePrice = int(item['salePrice'])
    except:
        salePrice = item['salePrice']
    if type(salePrice) != int or salePrice == None or salePrice == '':
        salePrice = 0
    try:
        photoPrice = int(item['photoPrice'])
    except:
        photoPrice = item['photoPrice']
    if type(photoPrice) != int or photoPrice == None or photoPrice == '':
        photoPrice = 0
    try:
        partyPrice = int(item['partyPrice'])
    except:
        photoPrice = item['photoPrice']
    if type(partyPrice) != int or partyPrice == None or partyPrice == '':
        partyPrice = 0
    try:
        oldPrice = int(item['oldPrice'])
    except:
        oldPrice = item['oldPrice']
    if type(oldPrice) != int or oldPrice == None or oldPrice == '':
        oldPrice = 0
    
    body = {
        "name" : name,
        "externalCode" : externalCode,
        "code": code,
        "article" : article,
        "salePrices": [
            {
                "priceType": {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/context/companysettings/pricetype/92624147-6543-11eb-0a80-07f1000909ab",
                        "type": "pricetype",
                        "mediaType": "application/json"
                    }
                },
                "value" : salePrice*100,
                "currency": {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/entity/currency/9260d73b-6543-11eb-0a80-07f1000909aa",
                        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/currency/metadata",
                        "type": "currency",
                        "mediaType": "application/json",
                    }
                }
            },
            {
                "priceType": {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/context/companysettings/pricetype/df4af656-d499-11ed-0a80-0df40029a0da",
                        "type": "pricetype",
                        "mediaType": "application/json"
                    }
                },
                "value" : photoPrice*100,
                "currency": {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/entity/currency/9260d73b-6543-11eb-0a80-07f1000909aa",
                        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/currency/metadata",
                        "type": "currency",
                        "mediaType": "application/json"
                    }
                }
            },
            {
                "priceType": {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/context/companysettings/pricetype/df4af77b-d499-11ed-0a80-0df40029a0db",
                        "type": "pricetype",
                        "mediaType": "application/json"
                    }
                },
                "value" : partyPrice*100,
                "currency": {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/entity/currency/9260d73b-6543-11eb-0a80-07f1000909aa",
                        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/currency/metadata",
                        "type": "currency",
                        "mediaType": "application/json",
                    }
                }
            },
            {
                "priceType": {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/context/companysettings/pricetype/10bfe5e0-b927-11ed-0a80-0d23003adcb4",
                        "type": "pricetype",
                        "mediaType": "application/json"
                    }
                },
                "value" : oldPrice*100,
                "currency": {
                    "meta": {
                        "href": "https://online.moysklad.ru/api/remap/1.2/entity/currency/9260d73b-6543-11eb-0a80-07f1000909aa",
                        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/currency/metadata",
                        "type": "currency",
                        "mediaType": "application/json",
                    }
                }
            }
        ],
        "productFolder": {
                "meta":{
                    "href": "https://online.moysklad.ru/api/remap/1.2/entity/productfolder/583f7744-d1df-11ed-0a80-0053005e66e5",
                    "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/productfolder/metadata",
                    "type": "productfolder",
                    "mediaType": "application/json"
                }
        }
    }
    
    r = put(url=url, headers=HEADERS, json=body)
    if r.status_code == 200:
        print(f'[{code}] Успешно обновлён')
        logging.info(f'[Update Item] {body["code"]}|{body["article"]}|{body["name"]}')
    elif r.status_code == 400:
        print(f'[{code}] Произошла ошибка, проверьте поля ')
        logging.error(f'[Update Item] Statuc Code: {r.status_code} {body["code"]}|{body["article"]}|{body["name"]}')
    else:
        print(f'[{code}] Произошла ошибка, и я не знаю какая...')
        logging.error(f'[Update Item] Statuc Code: {r.status_code} {body["code"]}|{body["article"]}|{body["name"]}')

if __name__ == '__main__': 
    # init_all_product_update()
    # init_all_order_update()
    # link = 'https://online.moysklad.ru/api/remap/1.2/entity/customerorder/3d4fd443-05e5-11ee-0a80-06f200099524'
    # set_selfprice_order(link)
    # print(set_rentable(link))
    ...