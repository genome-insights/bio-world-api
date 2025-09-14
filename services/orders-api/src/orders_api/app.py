from contextlib import asynccontextmanager

import fastapi
import uvicorn
from fastapi import FastAPI

from app.api.bioanalysis import router as bioanalysis_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    producer = AIOKafkaProducer()

app = fastapi.FastAPI(
    title="Orders API",
    version="0.1.0",
    description="Receives bioinformatics orders and publishes to Kafka",
    lifespan=lifespan
)

app.include_router(bioanalysis_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8001, reload=True)
