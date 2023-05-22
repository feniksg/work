from request_post_my_stock import update_status_order, change_active_rents, change_amount_product
from db import conn, cursor
from datetime import datetime

import time


def get_all_rents():
    sql = "SELECT * FROM my_stock"
    cursor.execute(sql)
    return cursor.fetchall()

def check_order(data):
    data = data[0]
    order_id = data[0]
    start = data[4]
    end = data[5]
    if start != '' and end !='':
        new_status = "Сдано"
        if check_status(order_id)[0][4] == "Забронирована":
            new_status = "В аренде"

        update_status_order(order_id, new_status) 
        update_status(order_id, new_status)
    else:
        update_status_order(order_id, 'Продано') #установить нужный статус
        update_status(order_id, 'Продано') #установить нужный статус


def save_all_rents(list_rents): 
    changed_fields = {}
    for this_rent in list_rents:
        sql = '''
            WITH ins AS (
                INSERT INTO my_stock (id_rent, fio_rent, phone_rent, status_rent, first_datetime_rent, second_datetime_rent, price_rent, id_product) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT ON CONSTRAINT id_rent_unique 
                DO UPDATE SET
                    fio_rent = excluded.fio_rent,
                    phone_rent = excluded.phone_rent,
                    status_rent = excluded.status_rent,
                    first_datetime_rent = excluded.first_datetime_rent,
                    second_datetime_rent = excluded.second_datetime_rent,
                    price_rent = excluded.price_rent,
                    id_product = excluded.id_product
                RETURNING *
            )
            SELECT 
                CASE 
                    WHEN my_stock.status_rent <> ins.status_rent THEN 'status_rent' 
                    ELSE NULL 
                END AS changed_field,
                my_stock.status_rent
            FROM my_stock
            JOIN ins USING (id_rent);
        '''
        cursor.execute(sql, this_rent)
        conn.commit()

        changed_field_db = cursor.fetchall()
        if changed_field_db:
            if changed_field_db[0][0]:
                changed_fields[changed_field_db[0][1]] = this_rent
    
    for changed_field in changed_fields.items():
        if changed_field[1][4] == "Забронирована" and changed_field[0] == "В аренде":
            for product in changed_field[1][-1]:
                change_amount_product(product)
                
        elif changed_field[1][4] == "В аренде" and changed_field[0] == "Задерживается":
            ...

        elif changed_field[1][4] == "В аренде" and changed_field[0] == "Сдано":
            ...

        elif changed_field[1][4] == "Задерживается" and changed_field[0] == "Сдано":
            ...

        else:
            ...


def check_timeout(): # TODO Запуск каждую минуту
    current_datetime = datetime.now()

    sql = "UPDATE my_stock SET status_rent = 'Задерживается' WHERE second_datetime_rent < %s AND status_rent <> 'Сдано' RETURNING *"
    cursor.execute(sql, (current_datetime,))

    updated_rows = cursor.fetchall()
    for row in updated_rows:
        # print(row)
        update_status_order(row[1], row[4])

    conn.commit()


def check_status(id_order):
    sql = '''SELECT * FROM my_stock WHERE id_rent = %s'''
    cursor.execute(sql, (id_order,))

    return cursor.fetchall()


def update_status(id_order, new_status):
    sql = '''UPDATE my_stock SET status_rent = %s WHERE id_rent = %s'''
    cursor.execute(sql, (new_status, id_order))
    conn.commit()

    sql = "SELECT * FROM my_stock WHERE id_rent = %s"
    cursor.execute(sql, (id_order,))

    # if new_status == "В аренде":
    #     for product in cursor.fetchall()[0][-1]:
    #         change_amount_product(product)
   

# def create_order(id_rent, fio_rent, phone_rent, status_rent, first_datetime_rent, second_datetime_rent, price_rent, id_product):
#     sql = '''
#             WITH ins AS (
#                 INSERT INTO my_stock (id_rent, fio_rent, phone_rent, status_rent, first_datetime_rent, second_datetime_rent, price_rent, id_product) 
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#         '''


def activ_rents(): # TODO Запуск каждые 5 минут
    current_datetime = datetime.now()

    sql = "SELECT * FROM my_stock WHERE first_datetime_rent < %s AND second_datetime_rent > %s AND status_rent <> 'Сдано'"
    cursor.execute(sql, (current_datetime, current_datetime))
    result = cursor.fetchall()
    dict_products = {}
    for order in result:
        for product_id in order[-1]:
            if product_id in dict_products:
                dict_products[product_id] += [{"start_datetime": order[5], "end_datetime": order[6], "fio_rent": order[2], "phone_rent": order[3]}]
            else:
                dict_products[product_id] = [{"start_datetime": order[5], "end_datetime": order[6], "fio_rent": order[2], "phone_rent": order[3]}]
    
    dict_products = dict(sorted(dict_products.items(), key=lambda x: x[1][0]['end_datetime']))
    return change_active_rents(dict_products)

        
 
if __name__ == "__main__":
    activ_rents()
    # start = time.time()
    # print(check_timeout())
    # print(time.time()-start)

