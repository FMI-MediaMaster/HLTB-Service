from fastapi import Request
from fastapi.responses import JSONResponse

from utils.custom_errors import HTTPError


async def error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPError as e:
        return JSONResponse(
            status_code=e.status_code,
            content=e.content,
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
        )
