from sqlalchemy.orm import Session

from app.models.denomination import Denomination


def get_all_denominations(db: Session) -> list[Denomination]:
    return db.query(Denomination).order_by(Denomination.value.desc()).all()


def update_denomination_counts(db: Session, denom_counts: dict[int, int]) -> None:
    """Add received cash denominations to shop's stock."""
    for value, count in denom_counts.items():
        if count <= 0:
            continue
        denom = db.query(Denomination).filter(Denomination.value == value).first()
        if denom:
            denom.count += count


def calculate_balance_denominations(db: Session, balance: int) -> dict[int, int]:
    """
    Calculate which denominations to return as change.
    Uses greedy approach from highest to lowest, limited by shop stock.
    """
    denominations = get_all_denominations(db)
    result = {}
    remaining = balance

    for denom in denominations:
        if remaining <= 0:
            break
        if denom.value > remaining or denom.count <= 0:
            continue

        needed = remaining // denom.value
        available = min(needed, denom.count)
        if available > 0:
            result[denom.value] = available
            remaining -= denom.value * available
            denom.count -= available

    return result
