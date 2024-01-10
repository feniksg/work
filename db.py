from settings import DB_HOST, DB_USER, DB_PASSWORD, DB_PORT, DB_NAME
import psycopg2

conn = psycopg2.connect(host="localhost",
                        user="admin",
                        password="qwertymama",
                        port="5432",
                        database="my_stock")

cursor = conn.cursor()


def delete_db():
    sql = "DROP TABLE my_stock"

    cursor.execute(sql)
    conn.commit()

    # cursor.close()
    # conn.close()


def create_db():
    alter_table_query = '''
        CREATE TABLE my_stock (
        id SERIAL PRIMARY KEY,
        id_rent INT,
        fio_rent TEXT,
        phone_rent TEXT,
        status_rent TEXT,
        first_datetime_rent TIMESTAMP,
        second_datetime_rent TIMESTAMP,
        price_rent FLOAT,
        id_product INT[]
    )
    '''

    cursor.execute(alter_table_query)
    conn.commit()

    # cursor.close()
    # conn.close()


def fix_db():
    sql = """
        ALTER TABLE my_stock
        ADD CONSTRAINT id_rent_unique UNIQUE (id_rent)
    """

    cursor.execute(sql)
    conn.commit()

    # cursor.close()
    # conn.close()


if __name__ == "__main__":
    delete_db()
    create_db()
    fix_db()