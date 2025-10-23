# test_conn.py
import os
import psycopg2
try:
    conn = psycopg2.connect("host=127.0.0.1 port=5432 dbname=vehicles user=app password=changeme")
    print("OK connected:", conn.get_dsn_parameters())
    conn.close()
except Exception as e:
    print("ERREUR:", e)
