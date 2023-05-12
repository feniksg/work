from handler import save_all_rents, update_status
from ms import get_orders


def upload_all_orders():
    list_rents = get_orders()
    return save_all_rents(list_rents)


def check_info_request(link):
    ...
    id_order, new_status = link
    update_status(id_order, new_status)
