from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.metrics import metrics_middleware, metrics_response

app = FastAPI(title="Async Shop API")
app.middleware("http")(metrics_middleware)


@app.get("/")
async def read_root():
    return {"message": "Async Shop API"}


@app.get("/metrics", include_in_schema=False)
async def metrics():
    return metrics_response()


app.include_router(api_router, prefix="/api/v1")