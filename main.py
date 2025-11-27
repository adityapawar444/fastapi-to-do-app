from fastapi import FastAPI

from routers import task
from db import (
    connect_to_db,
    Base,
    db_engine
)
from transaction_middleware import db_txn_middleware


db_engine = connect_to_db()
app = FastAPI(title="To Do List App")
app.middleware("http")(db_txn_middleware)
app.include_router(task.router)

# Base.metadata.crate_all(bind=db_engine)

@app.get("/")
async def root():
    return {"message": "App is Running"}
