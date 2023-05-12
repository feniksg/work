from db import conn, cursor
from datetime import datetime

from request_post_my_stock import update_status_order, change_active_rents, change_amount_product


def get_all_rents():
    sql = "SELECT * FROM my_stock"
    cursor.execute(sql)
    return cursor.fetchall()


def save_all_rents(list_rents): # TODO Запуск каждые 5 минут
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
        if changed_field[1][1] == "Забронирована" and changed_field[0] == "В аренде":
            ...
        elif changed_field[1][1] == "В аренде" and changed_field[0] == "В аренде, оплачено":
            ...
        elif changed_field[1][1] == "В аренде, оплачено" and changed_field[0] == "Задерживается":
            ...
        elif changed_field[1][1] == "Задерживается" and changed_field[0] == "Сдано":
            ...
        else:
            ...


def check_timeout(): # TODO Запуск каждую минуту
    current_datetime = datetime.now()

    sql = "UPDATE my_stock SET status_rent = 'Задерживается' WHERE second_datetime_rent < %s AND status_rent = 'В аренде, оплачен' RETURNING *"
    cursor.execute(sql, (current_datetime,))

    updated_rows = cursor.fetchall()
    for row in updated_rows:
        update_status_order(row[1], row[2])

    conn.commit()


def update_status(id_order, new_status):
    sql = '''UPDATE my_stock SET status_rent = %s WHERE id_rent = %s'''
    cursor.execute(sql, (new_status, id_order))
    conn.commit()

    sql = "SELECT * FROM my_stock WHERE id_rent = %s"
    cursor.execute(sql, (id_order,))

    if new_status == "В аренде" or new_status == "В аренде, оплачено":
        for product in cursor.fetchall()[-1]:
            change_amount_product(product)
   

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
                dict_products[product_id] += [{"start_datetime": order[5], "end_datetime": order[6], "full_name": order[2], "phone": order[3]}]
            else:
                dict_products[product_id] = [{"start_datetime": order[5], "end_datetime": order[6], "FIO": order[2], "phone": order[3]}]
    
    dict_products = sorted(dict_products.items(), key=lambda x: x[1][0]['end_datetime'])
    return change_active_rents(dict_products)


if __name__ == "__main__":
    current_time_1 = datetime(year=2021, month=1, day=3)
    current_time_1.strftime('%Y-%m-%d %H:%M:%S')
    current_time_2 = datetime(year=2025, month=1, day=3)
    current_time_2.strftime('%Y-%m-%d %H:%M:%S')

    list_rents = [["234", "Адрей", "+79992609773", "В аренде", current_time_1, current_time_2, "1233", [3543, 6532, 5853]]]
    # print(save_all_rents(list_rents))
    # print(get_all_rents())
    # check_timeout()
    print(activ_rents())

