# backend/app/services/search.py
import os
from typing import Dict, Any
from elasticsearch import Elasticsearch, exceptions as es_exceptions
import logging

logger = logging.getLogger(__name__)
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "http://127.0.0.1:9200")
ES_INDEX = os.getenv("ES_INDEX", "vehicles")

es = Elasticsearch(hosts=[ELASTIC_HOST])

class SearchService:
    index = ES_INDEX

    @staticmethod
    def _build_query(q: str = None, filters: Dict[str, Any] = None):
        body = {"query": {"bool": {}}}
        must = []
        filter_clauses = []

        if q:
            must.append({
                "multi_match": {
                    "query": q,
                    "fields": ["title^3", "make", "model"],
                    "type": "best_fields"
                }
            })

        if filters:
            # price range
            if "price_min" in filters or "price_max" in filters:
                rng = {}
                if filters.get("price_min") is not None:
                    rng["gte"] = int(filters["price_min"])
                if filters.get("price_max") is not None:
                    rng["lte"] = int(filters["price_max"])
                filter_clauses.append({"range": {"price": rng}})

            # year range
            if "year_min" in filters or "year_max" in filters:
                rng = {}
                if filters.get("year_min") is not None:
                    rng["gte"] = int(filters["year_min"])
                if filters.get("year_max") is not None:
                    rng["lte"] = int(filters["year_max"])
                filter_clauses.append({"range": {"year": rng}})

            if "make" in filters:
                filter_clauses.append({"term": {"make": filters["make"]}})
            if "model" in filters:
                filter_clauses.append({"term": {"model": filters["model"]}})

            # geo radius example (expects lat, lon, radius_km)
            if "lat" in filters and "lon" in filters and "radius_km" in filters:
                filter_clauses.append({
                    "geo_distance": {
                        "distance": f"{filters['radius_km']}km",
                        "location": {"lat": filters["lat"], "lon": filters["lon"]}
                    }
                })

        if must:
            body["query"]["bool"]["must"] = must
        if filter_clauses:
            body["query"]["bool"]["filter"] = filter_clauses
        if not must and not filter_clauses:
            body["query"] = {"match_all": {}}
        return body

    @staticmethod
    def search(q: str = None, filters: Dict[str, Any] = None, page: int = 1, size: int = 20) -> Dict[str, Any]:
        body = SearchService._build_query(q=q, filters=filters or {})
        from_ = (page - 1) * size
        try:
            resp = es.search(index=SearchService.index, body=body, from_=from_, size=size)
        except es_exceptions.NotFoundError:
            logger.info("ES index not found: %s", SearchService.index)
            return {"total": 0, "hits": []}
        except Exception as e:
            logger.exception("ES search error")
            raise

        hits = []
        total = resp.get("hits", {}).get("total", {}).get("value", 0)
        for h in resp.get("hits", {}).get("hits", []):
            hits.append({
                "id": h.get("_id"),
                "score": h.get("_score", 0.0),
                "source": h.get("_source", {})
            })
        return {"total": total, "hits": hits}
