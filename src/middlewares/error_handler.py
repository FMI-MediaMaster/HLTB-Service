from fastapi import Request
from fastapi.responses import JSONResponse

from utils.validation_error import ValidationError


async def error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except ValidationError as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)},
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
        )
