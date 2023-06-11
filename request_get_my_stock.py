from handler import save_all_rents, update_status, check_order
from ms import get_orders, put_main_data, get_link_from_payment, get_articles_from_order, set_selfprice, set_selfprice_order, set_rentable

def upload_all_orders():
    list_rents = get_orders()
    return save_all_rents(list_rents)


def check_info_request(link):
    set_selfprice_order(link)
    set_rentable(link)
    list_rents = put_main_data(link)
    save_all_rents(list_rents)

def get_articles(order_id):
    return get_articles_from_order(order_id)

def check_payment_request(link):
    orderlink = get_link_from_payment(link)
    data = put_main_data(orderlink)
    check_order(data)

def calc_additional_data_product(link):
    set_selfprice(link)

if __name__ == "__main__":
    upload_all_orders()