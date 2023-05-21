from requests import get, cookies
from ms import create_inpayment
import json, schedule, threading, time
PRO_LOGIN = 'vladakulikova@gmail.com'
PRO_PASSWORD = 'r4frvzf5aw'

def get_payments():
    url = 'https://kassa.produman.org/order/list/1'
    jar = cookies.RequestsCookieJar()    
    cookie_list = [
        {
            "domain": ".produman.org",
            "name": "__ddg1_",
            "path": "/",
            "value": "o3gceCDPLBphaLMoXLIB",
        },
        {
            "domain": "kassa.produman.org",
            "name": "PHPSESSID",
            "path": "/",
            "sameSite": "unspecified",
            "value": "9dok0lfk61aab7v2rs1up97ldk",
        },
        {
            "domain": "kassa.produman.org",
            "name": "REMEMBERME",
            "path": "/",
            "value": "App.Entity.Owner%3AdmxhZGFrdWxpa292YUBnbWFpbC5jb20~%3A1685208807%3AF6H8EbN67A7ZPnDJy0dNLfCPEA3p0EnAz_cEAepJ9Jk~pIqv3rgY76cEwAsp8cWhPVloMtP3r7lSwkDzwCRvG8Q~",
        }
    ]
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
            print(res[i]['number'][4:], res[i]['amount'])
            create_inpayment(res[i]['number'][4:], res[i]['amount'])
        save_payments(res)
        

if __name__ == '__main__':
    t1 = threading.Thread(target=schedule_check)
    t1.start()
