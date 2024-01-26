from dataclasses import dataclass
from ms import create_item, update_item, check_item
import requests, logging, csv, pickle, os, time, codecs

@dataclass
class Product():
    code: int
    name: str
    article: str
    price_sell: int = 0
    price_photo: int = 0
    price_party: int = 0
    price_old: int = 0
    currency:str = 'RUB'

class BtUpdater():
    csv_filename:str = None
    logger:logging.Logger = logging.getLogger('btlogger')
    product_list:list = None
    name:str = 'Bitrix Updater'
    update_queue:list = None

    def __init__(self, load_creation = True, dump_filename = 'default-state.pickle', csv_filename = 'bitrix/btupdater.csv', log_filename = 'bitrix/bt.log', csv_url = 'https://totaldress.ru/bitrix/catalog_export/moysklad.csv') -> None:
        if load_creation and os.path.exists(dump_filename):
            self._selfload()
        else:
            ##LOGGER
            self.logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler = logging.FileHandler(log_filename)
            file_handler.setLevel(logging.DEBUG)  
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            ##Файл с торговыми предложениями
            url = csv_url
            self.csv_url = csv_url
            headers = {'charset' : 'utf-8'} 
            content = requests.post(url=url,headers=headers).text.encode('iso-8859-1').decode('utf-8')
            with open(csv_filename, 'w+', encoding='utf-8') as file:
                file.write(content)
                self.csv_filename = file.name
                self.product_list = self._create_product_list()
            # self.csv_filename = csv_filename
            # self.product_list = self._create_product_list()

            self.update_queue = []
            self._selfsave()
        
    def _create_product_list(self, filename = '') -> None:
        if filename == '':
            filename = self.csv_filename
        products = {}
        with codecs.open(filename, 'r', "utf_8_sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                article = row['IP_PROP205']
                if article not in products:
                    products[article] = Product(
                        code=int(row['IE_XML_ID']),
                        name=row['IE_NAME'],
                        article=article,
                        price_sell=0 if row['CV_PRICE_1'] == '' else float(row['CV_PRICE_1']),
                        currency=row['CV_CURRENCY_1']
                    )
                else:
                    name = row['IE_NAME']
                    for prd in products.items():
                        if prd[1].name == name:
                            products[prd[0]].price_photo = 0 if row.get('CV_PRICE_2', 0) == '' else float(row.get('CV_PRICE_2', 0))
                            products[prd[0]].price_party = 0 if row.get('CV_PRICE_3', 0) == '' else float(row.get('CV_PRICE_3', 0))
                            products[prd[0]].price_old = 0 if row.get('CV_PRICE_4', 0) == '' else float(row.get('CV_PRICE_4', 0))
        del products['']
        return list(products.items())

    def _selfsave(self, filename = 'default-state.pickle') -> None:
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
        self.logger.info(f'Сохранение состояния в файл - {filename}')

    def _selfload(self, filename = 'default-state.pickle') -> None:
        with open(filename, 'rb') as f:
            instance:BtUpdater = pickle.load(f)
            self.csv_filename = instance.csv_filename
            self.logger = instance.logger
            self.csv_url = instance.csv_url
            self.name = instance.name
            self.product_list = instance.product_list
            self.update_queue = instance.update_queue
            #TODO: Дописать тут поля которые будут добавлены в класс
            self.logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler = logging.FileHandler('bitrix/bt.log')
            file_handler.setLevel(logging.DEBUG)  
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.logger.info(f'Загрузка состояния из файла - {filename}')

    def _file_equality(self, content:str) -> bool:
        with open(self.csv_filename, 'r', encoding='utf-8') as f:
            data = f.read()     
        return data.encode() == content.encode()

    def _get_dict(self) -> dict:
        return dict([(x[0], x[1]) for x in self.product_list])

    def mainloop(self):
        self._selfsave('pre_mainloop_autosave.pickle')
        self.logger.info('mainloop started.')
        try:
            url = self.csv_url
            headers = {'charset' : 'utf-8'} 
            prd_dict = self._get_dict()
            content = requests.post(url=url,headers=headers).text.encode('iso-8859-1').decode('utf-8')
            if not self._file_equality(content):
                with open('temp.csv', 'w+', encoding='utf-8') as file:
                    file.write(content)
                new_product_list = self._create_product_list('temp.csv')
                if not self.product_list == new_product_list:
                    #Формируем очередь
                    for item in new_product_list:
                        if item[0] in prd_dict.keys():
                            if prd_dict[item[0]] != item[1]:
                                self.update_queue.append(item[1])
                        else:
                            self.update_queue.append(item[1])
                    #Закончили формировать очередь
                self.product_list = new_product_list
                with open(self.csv_filename, 'w+', encoding='utf-8') as file:
                    file.write(content)
                self._update()
            self.logger.info('mainloop. files are equals. skipping...')
        except Exception as e:
            self.logger.info(f'{self.name}. mainloop - function. {e}')
            print(e)
            self._selfload('pre_mainloop_autosave.pickle')

    def _to_sklad(self, item):
        if check_item(item.code):
            update_item({"name" : item.name,"externalCode": item.code,"article" : item.article,"salePrice": item.price_sell,"photoPrice": item.price_photo,"partyPrice": item.price_party,"oldPrice": item.price_old,})
            self.logger.info(f'Updated - {item}')
        else:
            create_item({"name" : item.name,"externalCode": item.code,"article" : item.article,"salePrice": item.price_sell,"photoPrice": item.price_photo,"partyPrice": item.price_party,"oldPrice": item.price_old,})
            self.logger.info(f'Created - {item}')

    def _update(self) -> None:
        self._selfsave('pre_update_autosave.pickle')
        print(f'Queue length: {len(self.update_queue)}')
        while len(self.update_queue) != 0:
            item = self.update_queue[0]
            self.update_queue.remove(item)
            try:
                self._to_sklad(item)
            except Exception as e:
                self.logger.info(f'{self.name}. update - function. {e}')
                self.update_queue.append(item)
                self._selfsave('temp_update_autosave.pickle')
                print(f"""Something went wrong. Now on pause (5s).
                      Items in Queue left - {len(self.update_queue)}
                      """)
                time.sleep(5)
        self._selfsave()

    def __repr__(self) -> str:
        return self.name

if __name__ == '__main__':
    updater = BtUpdater()
    updater.mainloop()
    ...
