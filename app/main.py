import uvicorn
from fastapi import FastAPI

from app import models
from app.db import engine
from app.routes import events, metrics

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(events.router)
app.include_router(metrics.router)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
