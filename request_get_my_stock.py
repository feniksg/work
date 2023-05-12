from handler import save_all_rents, update_status, create_order
from ms import get_orders, put_main_data


def upload_all_orders():
    list_rents = get_orders()
    return save_all_rents(list_rents)


def check_info_request(link, type):
    if type == "update":
        update_status(put_main_data(link, type))
    elif type == "create":
        save_all_rents(put_main_data(link, type))