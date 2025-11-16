from fastapi import APIRouter, Request

from controllers.hltb import HltbController

router = APIRouter()


@router.get("/{method}")
async def hltb(method: str, request: Request):
    return await HltbController.handler(method, request)
