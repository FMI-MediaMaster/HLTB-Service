from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse


def unknown_endpoint_middleware(app):
    @app.exception_handler(404)
    async def unknown_endpoint_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Endpoint not found"},
        )
