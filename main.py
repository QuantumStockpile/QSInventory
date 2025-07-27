from pathlib import Path

from fastapi.responses import JSONResponse
import tortoise.exceptions
import uvicorn as uvicorn
from fastapi import FastAPI
from ms_core import setup_app

from app.dependencies import configure_auth
from app.settings import db_url, logger

application = FastAPI(
    title="QSInventory",
)

configure_auth("http://users_ms:8000", logger=logger)
tortoise_conf = setup_app(
    application, db_url, Path("app") / "routers", ["app.models", "aerich.models"]
)


@application.exception_handler(tortoise.exceptions.ValidationError)
async def exc_handler(request, exc: tortoise.exceptions.ValidationError):
    return JSONResponse(status_code=400, content={"msg": str(exc)})


if __name__ == "__main__":
    uvicorn.run("main:application", port=8000, reload=True)
