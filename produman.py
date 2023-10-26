from requests import get, cookies
from ms import create_inpayment
import json

def get_payments():
    url = 'https://kassa.produman.org/order/list/1'
    jar = cookies.RequestsCookieJar()    
    
    cookie_list = []
    with open('cookies_produman.json', 'r', errors='ignore') as f:
        cookie_list = json.loads(f.read())['cookie_list']

    for cookie in cookie_list:
        jar.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])
    
    response= get(url=url,cookies=jar)
    if response.status_code == 200:
        return response.json()['orders']
    else:
        return None

def save_payments(payments):
    with open('payments.json', 'w+') as f:
        json.dump(payments, f, indent=2)
    
def check_payments():
    payments = get_payments()
    res = {}
    for order in payments:
        res.update({
            str(order['number']):{
                'number': order['externalId'],
                'time': order['createdAt'],
                'amount': int(order['amount'])
                }
            }
        )
    with open('payments.json', 'r') as f:
        data = json.load(f)
    new_keys = list(res.keys())
    old_keys = list(data.keys())
    out = []
    for key in new_keys:
        if key not in old_keys:
            out.append(key)
    if out == []:
        return 'Nothing'
    else:
        for i in out:
            # print(res[i]['number'][4:], res[i]['amount'])
            create_inpayment(res[i]['number'][4:], res[i]['amount'])
        save_payments(res)
        

if __name__ == '__main__':
    print(get_payments())