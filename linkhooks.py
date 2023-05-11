from ms import MY_STORAGE_TOKEN
from requests import post, get

def link_webhook(target, type = 'product'):
    headers = {
        "Authorization": f"Bearer {MY_STORAGE_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "url": f'{target}/create',
        "action": "CREATE",
        "entityType": type
    }
    url = "https://online.moysklad.ru/api/remap/1.2/entity/webhook"
    r = post(url = url, headers=headers, json = body)
    if r.status_code == 200:
        print("[Product Create] Webhook created")
    else:
        print("[Product Create] Webhook creation failed", r.status_code)
    body = {
        "url": f'{target}/update',
        "action": "UPDATE",
        "entityType": type
    }
    r = post(url = url, headers=headers, json = body)
    if r.status_code == 200:
        print("[Product Update] Webhook created")
    else:
        print("[Product Update] Webhook creation failed", r.status_code)
    
def delete_webhooks():
    headers = {
        "Authorization": f"Bearer {MY_STORAGE_TOKEN}",
        "Content-Type": "application/json"
    }
    url = 'https://online.moysklad.ru/api/remap/1.2/entity/webhook'
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