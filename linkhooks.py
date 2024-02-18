from ms import MY_STORAGE_TOKEN
from requests import post, get

# http://c64d65bf721c.vps.myjino.ru/ - server url


def link_webhook(target, type = 'customerorder'):
    headers = {
        "Authorization": f"Bearer {MY_STORAGE_TOKEN}",
        "Content-Type": "application/json"
    }
    #Order create
    body = {
        "url": f'{target}/create/',
        "action": "CREATE",
        "entityType": type
    }
    url = "https://api.moysklad.ru/api/remap/1.2/entity/webhook"
    r = post(url = url, headers=headers, json = body)
    if r.status_code == 200:
        print("[Create order] Webhook created")
    else:
        print("[Create order] Webhook creation failed", r.status_code)
    #Order update
    body = {
        "url": f'{target}/update/',
        "action": "UPDATE",
        "entityType": type
    }
    r = post(url = url, headers=headers, json = body)
    if r.status_code == 200:
        print("[Update order] Webhook created")
    else:
        print("[Update order] Webhook creation failed", r.status_code)
    #Product create
    type = 'product'
    body = {
        "url": f'{target}/itemcreate/',
        "action": "CREATE",
        "entityType": type
    }
    r = post(url = url, headers=headers, json = body)
    if r.status_code == 200:
        print("[Create product] Webhook created")
    else:
        print("[Create product] Webhook creation failed", r.status_code)
    #Product update
    body = {
        "url": f'{target}/itemupdate/',
        "action": "UPDATE",
        "entityType": type
    }
    r = post(url = url, headers=headers, json = body)
    if r.status_code == 200:
        print("[Update product] Webhook created")
    else:
        print("[Update product] Webhook creation failed", r.status_code)
    #Payment create
    type = 'paymentin'
    body = {
        "url": f'{target}/payment/',
        "action": "CREATE",
        "entityType": type
    }
    r = post(url = url, headers=headers, json = body)
    if r.status_code == 200:
        print("[Payment] Webhook created")
    else:
        print("[Payment] Webhook creation failed", r.status_code)

def delete_webhooks():
    headers = {
        "Authorization": f"Bearer {MY_STORAGE_TOKEN}",
        "Content-Type": "application/json"
    }
    url = 'https://api.moysklad.ru/api/remap/1.2/entity/webhook'
    r = get(url = url, headers= headers)
    metas = []
    body = []
    if r.status_code == 200:
        data = r.json()['rows']
        for row in data:
            metas.append(row['meta'])
    for meta in metas:
        body.append({"meta" : meta})
    r = post(url=f'{url}/delete', headers=headers, json= body)
    print(r.status_code)
    
print("Application for link webhooks")
while True:
    a = input()
    if a == '/exit':
        quit(0)
    elif a.split(' ')[0] == '/link':
        b = a.split(' ')[1]
        link_webhook(b)
    elif a == '/clearhooks':
        delete_webhooks()
    elif a == '/help':
        print(f'WEBHOOK LINKER\n\t/link <URL> - Link webhook\n\t/clearhooks - Delete all linked webhooks\n\t/exit - Exit\n\t/help - Command information')
    else:
        print(f'ERROR, unknown command, type /help for show command list')