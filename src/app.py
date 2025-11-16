import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from middlewares.error_handler import error_handler
from routes.hltb import router as hltb_router

load_dotenv()
app = FastAPI()
app.middleware("http")(error_handler)
app.include_router(hltb_router)

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("PY_ENV", "production") == "development",
    )
