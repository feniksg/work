from db import conn, cursor
from datetime import datetime

from request_post_my_stock import update_status_order


def get_all_rents():
    sql = "SELECT * FROM my_stock"
    cursor.execute(sql)
    return cursor.fetchall()


def save_all_rents(list_rents):
    changed_fields = {}
    for this_rent in list_rents:
        sql = '''
            WITH ins AS (
                INSERT INTO my_stock (id_rent, status_rent, first_datetime_rent, second_datetime_rent, price_rent, id_product) 
                VALUES (%s, %s, %s, %s, %s, %s) 
                ON CONFLICT ON CONSTRAINT id_rent_unique 
                DO UPDATE SET
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
        if changed_field[1][1] == "ЗАБРОНИРОВАННО" and changed_field[0] == "В АРЕНДЕ":
            ...
        elif changed_field[1][1] == "В АРЕНДЕ" and changed_field[0] == "В АРЕНДЕ ОПЛАЧЕНО":
            ...
        elif changed_field[1][1] == "В АРЕНДЕ ОПЛАЧЕНО" and changed_field[0] == "ЗАДЕРЖИВАЕТСЯ":
            ...
        elif changed_field[1][1] == "ЗАДЕРЖИВАЕТСЯ" and changed_field[0] == "СДАНО":
            ...
        else:
            ...


def check_timeout():
    current_datetime = datetime.now()

    sql = "UPDATE my_stock SET status_rent = 'ЗАДЕРЖИВАЕТСЯ' WHERE second_datetime_rent < %s AND status_rent = 'В АРЕНДЕ' RETURNING *"
    cursor.execute(sql, (current_datetime,))

    updated_rows = cursor.fetchall()
    for row in updated_rows:
        update_status_order(row[1], row[2])

    conn.commit()


def update_status(id_order, new_status):
    sql = '''UPDATE my_stock SET status_rent = %s WHERE id_rent = %s'''
    cursor.execute(sql, (new_status, id_order))
    conn.commit()


def activ_rents():
    ...


if __name__ == "__main__":
    current_time = datetime.now()
    current_time.strftime('%Y-%m-%d %H:%M:%S')
    list_rents = [["23412", "В АРЕНДЕ", current_time, current_time, "1233", [3543, 6532]]]
    print(save_all_rents(list_rents))
    print(get_all_rents())
    check_timeout()

