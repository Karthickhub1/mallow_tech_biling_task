import logging

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from app.core.database import Base, engine
from app.routers import billing, history, products

logging.basicConfig(level=logging.INFO)

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Billing System")

# Include routers
app.include_router(products.router)
app.include_router(billing.router)
app.include_router(history.router)


@app.get("/")
def root():
    return RedirectResponse(url="/billing")
