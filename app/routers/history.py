from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.billing_service import get_invoice_by_id, get_invoices_by_email

router = APIRouter(prefix="/history", tags=["Purchase History"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def history_page(request: Request):
    return templates.TemplateResponse("history.html", {"request": request, "invoices": None, "selected": None, "email": ""})


@router.get("/search", response_class=HTMLResponse)
def search_history(request: Request, email: str = "", db: Session = Depends(get_db)):
    invoices = get_invoices_by_email(db, email) if email.strip() else []
    return templates.TemplateResponse(
        "history.html",
        {"request": request, "invoices": invoices, "selected": None, "email": email},
    )


@router.get("/invoice/{invoice_id}", response_class=HTMLResponse)
def view_invoice(request: Request, invoice_id: int, email: str = "", db: Session = Depends(get_db)):
    invoices = get_invoices_by_email(db, email) if email.strip() else []
    selected = get_invoice_by_id(db, invoice_id)
    return templates.TemplateResponse(
        "history.html",
        {"request": request, "invoices": invoices, "selected": selected, "email": email},
    )
