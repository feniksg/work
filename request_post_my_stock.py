import requests
from ms import set_state, leftovers_plus, write_active_rents

def update_status_order(id_order, new_status):
    set_state(id_order, new_status)


def change_active_rents(dict_products):
    write_active_rents(dict_products)


def change_amount_product(id_product):
    leftovers_plus(id_product)