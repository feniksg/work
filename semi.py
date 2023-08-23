from ms import get_orders, BASE_URL, HEADERS
from json import dump,load
from requests import get, delete


def download_orders():
    limit = 500
    offset = 0
    url_api = 'entity/customerorder' 
    body = {
        'limit': limit,
        'offset': offset
    }

    response = get(url=f'{BASE_URL}{url_api}/?limit={limit}&offset={offset}',headers=HEADERS, json= body)
    if response.status_code == 200:
        data = response.json()['rows']
    
    r = data
    while len(r) == limit:
        offset+=500
        body['offset'] = offset
        r = get(url=f'{BASE_URL}{url_api}/?limit={limit}&offset={offset}',headers=HEADERS, json= body).json()['rows']
        data+=r
    
    with open('order.json', 'w+', encoding='utf-8') as file:
        dump(data, file, indent= 2, ensure_ascii=False)
    print(len(data))

def delete_doubles():
    url_api = 'entity/customerorder/' 
    data = []
    with open('order.json', 'r', encoding='utf-8') as file:
        data = load(file)
    check = []
    for item in data:
        order_id = item['id']
        url = f'{BASE_URL}{url_api}{order_id}'
        moment = item['moment']
        order_sum = item['sum']
        agent = item['agent']['meta']['href']
        current = (moment,order_sum,agent)
        if current in check:
            response = delete(url=url, headers=HEADERS)
            if response.status_code != 200:
                print(response.text)
            else:
                print(f'Deleted - {current}')
        else:
            print(f'Added - {current}')
            check.append(current)
    with open('uniq.json', 'w+', encoding='utf-8') as file:
        dump(check, file, ensure_ascii=False, indent= 2)
    print(len(check)) 

if __name__ == '__main__':
    download_orders()
    delete_doubles()
    
        