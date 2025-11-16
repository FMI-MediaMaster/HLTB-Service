from fastapi import Request

from services.hltb import HltbService


class HltbController:
    @staticmethod
    async def handler(method: str, request: Request):
        return await HltbService().handle(method, dict(request.query_params))
