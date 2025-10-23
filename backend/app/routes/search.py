# backend/app/routes/search.py
from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional, Dict, Any
from app.services.search import SearchService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["search"])

@router.post("/search")
async def search_post(payload: Dict[str, Any]):
    """
    Accept generic JSON body. Expected shape:
    { "q": "...", "filters": {...}, "page": 1, "size": 20 }
    """
    try:
        q = payload.get("q")
        filters = payload.get("filters", {}) or {}
        page = int(payload.get("page", 1) or 1)
        size = int(payload.get("size", 20) or 20)
    except Exception as e:
        logger.exception("Malformed search payload")
        raise HTTPException(status_code=422, detail="Malformed search payload")

    try:
        res = SearchService.search(q=q, filters=filters, page=page, size=size)
        return res
    except Exception as e:
        logger.exception("SearchService error")
        raise HTTPException(status_code=500, detail="Search error")

@router.get("/search")
async def search_get(
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    # you can add other query params for filters (make, model, price_min etc)
    make: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    price_min: Optional[int] = Query(None),
    price_max: Optional[int] = Query(None),
):
    filters = {}
    if make:
        filters["make"] = make
    if model:
        filters["model"] = model
    if price_min is not None or price_max is not None:
        rng = {}
        if price_min is not None:
            rng["price_min"] = price_min
        if price_max is not None:
            rng["price_max"] = price_max
        filters.update(rng)
    try:
        res = SearchService.search(q=q, filters=filters, page=page, size=size)
        return res
    except Exception:
        logger.exception("SearchService error (GET)")
        raise HTTPException(status_code=500, detail="Search error")
