"""
Aggregateur de tous les routers API
"""

from fastapi import APIRouter

from app.api.tenants import router as auth_router, tenants_router
from app.api.catalog import router as catalog_router
from app.api.dashboard import router as dashboard_router

api_router = APIRouter()

# OAuth + auth
api_router.include_router(auth_router)
# Tenants management
api_router.include_router(tenants_router)
# Catalog upload + products
api_router.include_router(catalog_router)
# Dashboard + analytics
api_router.include_router(dashboard_router)
