from handler import save_all_rents, update_status, check_order
from ms import get_orders, put_main_data, get_link_from_payment
from request_post_my_stock import update_status

def upload_all_orders():
    list_rents = get_orders()
    return save_all_rents(list_rents)


def check_info_request(link):
    list_rents = put_main_data(link)
    save_all_rents(list_rents)

def check_payment_request(link):
    orderlink = get_link_from_payment(link)
    data = put_main_data(orderlink)
    check_order(data)

if __name__ == "__main__":
    upload_all_orders()