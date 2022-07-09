from logging import Logger, getLogger

from fastapi import APIRouter

from web_log_collector.api.web import ROUTER as WEB_ROUTER

LOG: Logger = getLogger(__name__)

API_ROUTER = APIRouter()
API_ROUTER.include_router(WEB_ROUTER, tags=['web'])
