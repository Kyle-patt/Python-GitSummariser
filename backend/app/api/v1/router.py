"""
Aggregated API v1 Router.
"""
from fastapi import APIRouter
from backend.app.api.v1.endpoints import summaries, history, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(summaries.router)
api_router.include_router(history.router)

