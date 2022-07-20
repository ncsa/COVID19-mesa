#!/usr/bin/python
import psycopg2
from config import config


def insert_data(data):
    """ insert a new vendor into the vendors table """
    sql = "INSERT INTO summary(step, cummul_priv_value, cummul_publ_value, cummul_test_cost, rt, employed, unemployed) VALUES(%s, %s, %s, %s, %s, %s, %s)"
    conn = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, data)
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    # insert one vendor
    insert_data((0, 0.0, 0.0, 0.0, 0, 200 ,0))
    