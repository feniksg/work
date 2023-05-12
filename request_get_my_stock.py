from handler import save_all_rents
from ms import get_orders


def upload_all_orders():
    list_rents = get_orders()
    return save_all_rents(list_rents)


