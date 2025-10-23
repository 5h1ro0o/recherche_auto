# check_db.py
import psycopg2
try:
    conn = psycopg2.connect("host=127.0.0.1 port=5432 dbname=vehicles user=app password=changeme")
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    tables = cur.fetchall()
    print("Tables in public schema:", [t[0] for t in tables])
    cur.execute("SELECT * FROM alembic_version;")
    print("alembic_version:", cur.fetchall())
    cur.close()
    conn.close()
except Exception as e:
    print("ERREUR:", e)
