"""Knowledge search endpoint."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.agents.search.agent import SearchAgent
from app.schemas.search import SearchRequest, SearchResult

logger = logging.getLogger(__name__)
router = APIRouter()
_search = SearchAgent()


@router.post("/search", response_model=SearchResult)
async def search_knowledge(request: SearchRequest) -> SearchResult:
    """Search the institutional knowledge base."""
    try:
        return _search.run(request)
    except Exception:
        logger.exception("Knowledge search request failed")
        raise HTTPException(status_code=500, detail="AI request failed") from None
