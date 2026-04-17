import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.services.billing_service import generate_bill
from app.services.denomination_service import get_all_denominations
from app.services.product_service import get_all_products
from app.utils.email import send_invoice_email

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/billing", tags=["Billing"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def billing_page(request: Request, db: Session = Depends(get_db)):
    products = get_all_products(db)
    denominations = get_all_denominations(db)
    return templates.TemplateResponse(
        "billing_form.html",
        {
            "request": request,
            "products": products,
            "denominations": denominations,
            "default_denoms": settings.DENOMINATIONS,
        },
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate_bill_view(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    form_data = await request.form()

    customer_email = form_data.get("customer_email", "").strip()
    if not customer_email:
        raise HTTPException(status_code=400, detail="Customer email is required")

    items = []
    index = 0
    while True:
        pid = form_data.get(f"product_id_{index}")
        qty = form_data.get(f"quantity_{index}")
        if pid is None:
            break
        if pid.strip() and qty:
            items.append({"product_id": pid.strip(), "quantity": int(qty)})
        index += 1

    if not items:
        raise HTTPException(status_code=400, detail="At least one product is required")

    denominations_received = {}
    for denom_value in settings.DENOMINATIONS:
        count_str = form_data.get(f"denom_{denom_value}", "0")
        count = int(count_str) if count_str.strip() else 0
        if count > 0:
            denominations_received[denom_value] = count

    cash_paid = float(form_data.get("cash_paid", 0))

    result = generate_bill(db, customer_email, items, denominations_received, cash_paid)

    invoice = result["invoice"]
    balance_denoms = result["balance_denominations"]

    response_html = templates.TemplateResponse(
        "bill_result.html",
        {
            "request": request,
            "invoice": invoice,
            "balance_denominations": balance_denoms,
        },
    )

    background_tasks.add_task(send_invoice_email, customer_email, invoice, balance_denoms)

    return response_html
