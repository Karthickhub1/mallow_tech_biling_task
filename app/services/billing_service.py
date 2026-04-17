import math

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.invoice import Invoice, InvoiceItem
from app.models.product import Product
from app.services.denomination_service import (
    calculate_balance_denominations,
    update_denomination_counts,
)
from app.utils.bill_logger import get_bill_logger


def generate_bill(
    db: Session,
    customer_email: str,
    items: list[dict],  # [{"product_id": str, "quantity": int}]
    denominations_received: dict[int, int],  # {500: 2, 100: 1, ...}
    cash_paid: float,
) -> dict:
    """
    Generate a bill: validate products, calculate totals, create invoice,
    update stock and denominations, compute balance change.
    """
    log = get_bill_logger()
    log.info("--------------- start generate ---------------")
    log.info(
        "input customer=%s items=%s denominations=%s cash_paid=%s",
        customer_email, items, denominations_received, cash_paid,
    )

    try:
        result = _generate_bill_impl(
            db, customer_email, items, denominations_received, cash_paid
        )
        invoice = result["invoice"]
        log.info(
            "success invoice_id=%s total=%s balance=%s balance_denoms=%s",
            invoice.id, invoice.rounded_net_price, invoice.balance,
            result["balance_denominations"],
        )
        return result
    except Exception as e:
        log.exception("failure: %s", e)
        raise
    finally:
        log.info("--------------- end generate ---------------")


def _generate_bill_impl(
    db: Session,
    customer_email: str,
    items: list[dict],
    denominations_received: dict[int, int],
    cash_paid: float,
) -> dict:
    log = get_bill_logger()
    invoice_items = []
    total_without_tax = 0.0
    total_tax = 0.0

    log.debug("step=validate_items count=%s", len(items))
    for item in items:
        product = db.query(Product).filter(Product.product_id == item["product_id"]).first()
        if not product:
            log.debug("product_not_found product_id=%s", item["product_id"])
            raise HTTPException(
                status_code=400,
                detail=f"Product '{item['product_id']}' not found",
            )
        if product.available_stocks < item["quantity"]:
            log.debug(
                "insufficient_stock product_id=%s available=%s requested=%s",
                product.product_id, product.available_stocks, item["quantity"],
            )
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Insufficient stock for '{product.name}'. "
                    f"Available: {product.available_stocks}, Requested: {item['quantity']}"
                ),
            )

        purchase_price = product.price * item["quantity"]
        tax_amount = purchase_price * (product.tax_percentage / 100)
        total_price = purchase_price + tax_amount

        log.debug(
            "line_item product_id=%s qty=%s unit_price=%s purchase_price=%s tax=%s total=%s",
            product.product_id, item["quantity"], product.price,
            round(purchase_price, 2), round(tax_amount, 2), round(total_price, 2),
        )

        total_without_tax += purchase_price
        total_tax += tax_amount

        invoice_items.append(
            InvoiceItem(
                product_id=product.product_id,
                product_name=product.name,
                unit_price=product.price,
                quantity=item["quantity"],
                purchase_price=round(purchase_price, 2),
                tax_percentage=product.tax_percentage,
                tax_amount=round(tax_amount, 2),
                total_price=round(total_price, 2),
            )
        )

    net_price = total_without_tax + total_tax
    rounded_net_price = math.ceil(net_price)
    balance = cash_paid - rounded_net_price

    log.debug(
        "totals total_without_tax=%s total_tax=%s net_price=%s rounded=%s balance=%s",
        round(total_without_tax, 2), round(total_tax, 2),
        round(net_price, 2), rounded_net_price, balance,
    )

    if balance < 0:
        log.debug(
            "insufficient_payment required=%s paid=%s",
            rounded_net_price, cash_paid,
        )
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient payment. Bill total: {rounded_net_price}, Paid: {cash_paid}",
        )

    invoice = Invoice(
        customer_email=customer_email,
        total_without_tax=round(total_without_tax, 2),
        total_tax=round(total_tax, 2),
        net_price=round(net_price, 2),
        rounded_net_price=rounded_net_price,
        cash_paid=cash_paid,
        balance=balance,
    )
    invoice.items = invoice_items
    db.add(invoice)
    log.debug("step=persist_invoice items=%s", len(invoice_items))

    for item in items:
        product = db.query(Product).filter(Product.product_id == item["product_id"]).first()
        product.available_stocks -= item["quantity"]
        log.debug(
            "stock_deducted product_id=%s remaining=%s",
            product.product_id, product.available_stocks,
        )

    update_denomination_counts(db, denominations_received)
    log.debug("step=denominations_updated received=%s", denominations_received)

    balance_denoms = calculate_balance_denominations(db, int(balance))
    log.debug("step=balance_denominations_calculated result=%s", balance_denoms)

    db.commit()
    db.refresh(invoice)
    log.debug("step=committed invoice_id=%s", invoice.id)

    return {
        "invoice": invoice,
        "balance_denominations": balance_denoms,
    }


def get_invoices_by_email(db: Session, email: str) -> list[Invoice]:
    return (
        db.query(Invoice)
        .filter(Invoice.customer_email == email)
        .order_by(Invoice.created_at.desc())
        .all()
    )


def get_invoice_by_id(db: Session, invoice_id: int) -> Invoice | None:
    return db.query(Invoice).filter(Invoice.id == invoice_id).first()
