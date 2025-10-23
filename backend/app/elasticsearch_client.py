from elasticsearch import Elasticsearch
import os
es = Elasticsearch(os.getenv("ELASTIC_HOST", "http://localhost:9200"))
