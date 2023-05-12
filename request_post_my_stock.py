import requests
from ms import set_state

def update_status_order(id_order, new_status):
    set_state(id_order, new_status)


