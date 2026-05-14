from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter

app = FastAPI()

# 1. Стандартні метрики (час запиту, кількість 200/404 помилок тощо)
Instrumentator().instrument(app).expose(app)

# 2. КАСТОМНА МЕТРИКА (приклад для вашого GTB: кількість вгаданих блоків)
BLOCKS_GUESSED_TOTAL = Counter(
    "blocks_guessed_total",
    "Total number of successfully guessed blocks"
)

@app.post("/guess")
def guess_block(block_id: str):
    # Логіка вгадування...
    BLOCKS_GUESSED_TOTAL.inc() # Збільшуємо лічильник на 1
    return {"status": "success"}