from handler import save_all_rents, update_status
from ms import get_orders, put_main_data


def upload_all_orders():
    list_rents = get_orders()
    return save_all_rents(list_rents)


def check_info_request(link):
    id_order, new_status = put_main_data(link)
    update_status(id_order, new_status)
