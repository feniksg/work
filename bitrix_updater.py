from csv import reader
from requests import post, exceptions
from ms import create_item,update_item, check_item
from os.path import exists
import logging, json, time




logger = logging.getLogger('btlogger')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('bitrix/bt.log')
file_handler.setLevel(logging.DEBUG)  
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class Product(object):
    def __init__(self, id, name, article, sell_price, photo_price, party_price, old_price):
        self.id = id
        self.name = name
        self.article = article
        if sell_price == '':
            self.sell_price = 0
        else:
            self.sell_price = int(sell_price[:-3])
        if photo_price == '':
            self.photo_price = 0
        else:
            self.photo_price = int(photo_price[:-3])
        if party_price == '':
            self.party_price = 0
        else:
            self.party_price = int(party_price[:-3])
        if old_price == '':
            self.old_price = 0
        else:
            self.old_price = int(old_price[:-3])
        self.currency = 'RUB'
        
    def __repr__(self) -> str:
        return f'prdct&{self.id}${self.name}${self.article}${self.sell_price}${self.photo_price}${self.party_price}${self.old_price}'

def parse(data):
    first = True
    items = []
    names = []
    artiles = []
    for row in data:
        if first:
            first = False
            continue
        if  row[1] not in names and row[2] != '':
            items.append(Product(row[0],row[1],row[2],row[3],row[5],row[7],row[9]))
            names.append(row[1])
            artiles.append(row[2])
        elif row[1] in names and row[2] not in artiles and row[2] != '':
            items.append(Product(row[0],row[1],row[2],row[3],row[5],row[7],row[9]))
            artiles.append(row[2])
        else:
            for item in items:
                if item.name == row[1]:
                    if row[5] != '':
                        item.photo_price = int(row[5][:-3])
                    if row[7] != '':
                        item.party_price = int(row[7][:-3])
                    if row[9] != '':
                        item.old_price = int(row[9][:-3])

    ddict = {}
    for item in items:
        ddict[f'{item.id}'] = f'{item}'

    return ddict, items

def to_sklad(item, mode):
    if mode == 'update':
                if check_item(item.id):
                    update_item({"name" : item.name,"externalCode": item.id,"article" : item.article,"salePrice": item.sell_price,"photoPrice": item.photo_price,"partyPrice": item.party_price,"oldPrice": item.old_price,})
    elif mode == 'create':
        create_item({"name" : item.name,"externalCode": item.id,"article" : item.article,"salePrice": item.sell_price,"photoPrice": item.photo_price,"partyPrice": item.party_price,"oldPrice": item.old_price,})

def scan():
    if exists('bitrix/temp2.csv'):
        with open('bitrix/temp2.csv', 'r', encoding='utf-8') as f:
            data = f.read()
        with open('bitrix/temp.csv', 'w+', encoding='utf-8') as f:
            f.write(data)

    url = 'https://totaldress.ru/bitrix/catalog_export/moysklad.csv'
    header = {
        "charset" : "utf-8"
    }
    response = post(url=url,headers=header).text.encode('iso-8859-1').decode('utf-8')

    is_active = True
    with open("bitrix/temp2.csv", 'w+', encoding='utf-8') as file:
        file.write(response)
    if exists('bitrix/temp.csv'):
        with open('bitrix/temp2.csv', 'r', encoding='utf-8') as file:
                check2 = file.read()
        with open('bitrix/temp.csv', 'r', encoding='utf-8') as file:
                check1 = file.read()
        # is_active = check1 != check2

    if is_active:
        with open('bitrix/temp2.csv', 'r', encoding='utf-8') as file:
            data = list(reader(file))

        ddict, items = parse(data)    

        if not exists('bitrix/bt_items.json'):
            with open('bitrix/bt_items.json', 'w+', encoding='utf-8') as file:
                json.dump(ddict, file, ensure_ascii=False, indent=2)
        else:
            with open('bitrix/bt_items.json', 'r', encoding='utf-8') as file:
                oldddict = json.load(file)
            keys = oldddict.keys()
            for item in items:
                    if int(item.id) < 12355:
                        continue
                    try:
                        key = str(item.id)
                        if key in keys:
                            if oldddict[key] != str(item):
                                to_sklad(item, 'update')
                                logger.info(f"Item {key}, updated.")
                            else:
                                logger.info(f"Item {key}, don't need update.")
                        else:
                            to_sklad(item, 'create')
                            logger.info(f"Item {key}, created.")
                    except exceptions.ConnectionError:
                        time.sleep(5)
                        key = str(item.id)
                        if key in keys:
                            if oldddict[key] != str(item):
                                to_sklad(item, 'update')
                                logger.info(f"Item {key}, updated.")
                            else:
                                logger.info(f"Item {key}, don't need update.")
                        else:
                            to_sklad(item, 'create')
                            logger.info(f"Item {key}, created.")
            with open('bitrix/bt_items.json', 'w+', encoding='utf-8') as file:
                json.dump(ddict, file, ensure_ascii=False, indent=2)
    else:
        print("Updates not detected")

if __name__ == '__main__':
    scan()
    ...
    
