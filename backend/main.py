from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api import auth, cases, dashboard, devices, faults, files, health, inspections, knowledge, maintenance, qa, search, users
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="面向电梯扶梯维保场景的多模态知识检索与标准化作业辅助系统",
        version="0.1.0",
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "message": exc.detail, "data": {}},
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"code": 422, "message": "请求参数校验失败", "data": exc.errors()},
        )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(cases.router)
    app.include_router(dashboard.router)
    app.include_router(devices.router)
    app.include_router(faults.router)
    app.include_router(files.router)
    app.include_router(inspections.router)
    app.include_router(knowledge.router)
    app.include_router(maintenance.router)
    app.include_router(search.router)
    app.include_router(qa.router)
    app.include_router(users.router)

    return app


app = create_app()
