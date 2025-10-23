# backend/app/es_setup.py
import os
import sys
from elasticsearch import Elasticsearch, exceptions

# charge la variable d'env ELASTIC_HOST si présente, sinon fallback
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "http://127.0.0.1:9200")
INDEX_NAME = "vehicles"

def get_es_client():
    # si tu as besoin d'auth (user/pass), tu peux décoder depuis env:
    # es_user = os.getenv("ELASTIC_USER")
    # es_pass = os.getenv("ELASTIC_PASSWORD")
    # return Elasticsearch(hosts=[ELASTIC_HOST], basic_auth=(es_user, es_pass))
    return Elasticsearch(hosts=[ELASTIC_HOST])

def main():
    es = get_es_client()

    # test ping / connection
    try:
        if not es.ping():
            print(f"Impossible de contacter Elasticsearch sur {ELASTIC_HOST}")
            return 1
    except exceptions.AuthenticationException:
        print("Erreur d'authentification auprès d'Elasticsearch.")
        return 1
    except Exception as e:
        print("Erreur connexion Elasticsearch:", e)
        return 1

    mapping = {
      "mappings": {
        "properties": {
          "title": {"type": "text"},
          "make": {"type": "keyword"},
          "model": {"type": "keyword"},
          "price": {"type": "integer"},
          "mileage": {"type": "integer"},
          "year": {"type": "integer"},
          "location": {"type": "geo_point"},
          "posted_date": {"type": "date"},
          "source_ids": {"type": "object"},
          "score": {"type": "float"}
        }
      }
    }

    try:
        exists = es.indices.exists(index=INDEX_NAME)
        if exists:
            print(f"Index '{INDEX_NAME}' existe déjà.")
        else:
            es.indices.create(index=INDEX_NAME, body=mapping)
            print(f"Index '{INDEX_NAME}' créé avec mapping.")
    except Exception as e:
        print("Erreur lors de la création de l'index:", e)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
