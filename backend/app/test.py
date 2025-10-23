# backend/app/es_test_verbose.py
import os, traceback
from elasticsearch import Elasticsearch, exceptions

def main():
    host = os.getenv("ELASTIC_HOST", "http://127.0.0.1:9200")
    print("ELASTIC_HOST:", host)
    try:
        # try different client inits if needed
        es = Elasticsearch(hosts=[host])
        print("Elasticsearch client:", es)
        print("ping:", es.ping())
        print("info:", es.info())
    except Exception as e:
        print("Exception raised when contacting ES:")
        traceback.print_exc()

if __name__ == "__main__":
    main()
