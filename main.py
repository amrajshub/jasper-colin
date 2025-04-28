"""
monitoring? graylog?

caching and quees?
Explain how you would implement caching (e.g., for frequently accessed tasks) and message queuing (e.g., for background task processing).


HLD
Provide a diagram of the architecture (describe in text form if unable to draw).
"""

import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from database.models import HttpLogs
from utils.keycloak import auth_middleware
from api.routers.tasks import router as TaskRouter

logger = logging.getLogger("app")


app = FastAPI()
app.include_router(router=TaskRouter, prefix="/task")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(str(exc))
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "method": request.method,
            "url": str(request.url),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc),
            "method": request.method,
            "url": str(request.url),
        },
    )


@app.middleware("http")
async def add_keycloak_auth(request: Request, call_next):
    request_body = await request.body()
    request_data = request.path_params or request.query_params or request_body
    log = HttpLogs(
        request=request_data, url=request.url, entity_type=None, entity_id=None
    )
    await auth_middleware(request)
    response = await call_next(request)
    log.response = response
    logger.info(f"Call logged for the request: {request_data} and response: {response}")
    return response


@app.get("/user-data")
async def user_data(request: Request):
    user_info = request.state.user_info
    return {"message": "Hello, this is a protected route!", "user_info": user_info}
