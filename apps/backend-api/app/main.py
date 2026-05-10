from fastapi import FastAPI  

from app.api.v1.router import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="EduAdvisorBot API",
        version="0.1.0", 
        description="Web backend for EduAdvisorBot with NLP intent parsing.",
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()


