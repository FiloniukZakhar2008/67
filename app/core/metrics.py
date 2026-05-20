from time import perf_counter

from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import OrderItem, Product


HTTP_REQUESTS_TOTAL = Counter(
    "fastapi_http_requests_total",
    "Total number of HTTP requests served by the FastAPI application.",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "fastapi_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "path"],
)

SHOP_ORDERS_CREATED_TOTAL = Counter(
    "shop_orders_created",
    "Total number of created purchases/orders.",
)

SHOP_PURCHASES_TOTAL_PRICE = Counter(
    "shop_purchases_total_price",
    "Cumulative price of all created purchases.",
)

SHOP_LAST_PURCHASE_PRICE = Gauge(
    "shop_last_purchase_price",
    "Total price of the most recently created purchase.",
)


async def metrics_middleware(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)

    start = perf_counter()
    response = await call_next(request)
    duration = perf_counter() - start
    route = request.scope.get("route")
    path = getattr(route, "path", request.url.path)

    HTTP_REQUESTS_TOTAL.labels(request.method, path, str(response.status_code)).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(request.method, path).observe(duration)
    return response


def metrics_response() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


async def record_order_metrics(db: AsyncSession, order_id: int) -> None:
    result = await db.execute(
        select(OrderItem.quantity, Product.price)
        .join(Product, Product.id == OrderItem.product_id)
        .where(OrderItem.order_id == order_id)
    )
    total_price = sum(float(quantity) * float(price) for quantity, price in result.all())

    SHOP_ORDERS_CREATED_TOTAL.inc()
    SHOP_PURCHASES_TOTAL_PRICE.inc(total_price)
    SHOP_LAST_PURCHASE_PRICE.set(total_price)