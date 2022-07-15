import os

import psycopg2

def get_db_connection():
	conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
	return conn


def get_cursor():
    conn = get_db_connection()
    cur = conn.cursor()
    return conn,cur

def close_cursor(conn, cur):
    cur.close()
    conn.close()