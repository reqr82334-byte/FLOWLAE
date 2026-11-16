from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import require_admin
from ..models import Order
from ..schemas import OrderIn, OrderOut, StatusIn
router = APIRouter()
VALID_STATUSES = {"awaiting_payment", "paid", "purchased", "at_warehouse", "shipped", "delivered"}
@router.post("", response_model=OrderOut)
def create_order(payload: OrderIn, db: Session = Depends(get_db)):
    item = Order(**payload.model_dump()); db.add(item); db.commit(); db.refresh(item); return item
@router.get("", response_model=list[OrderOut], dependencies=[Depends(require_admin)])
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).order_by(Order.created_at.desc()).limit(100).all()
@router.patch("/{order_id}/status", response_model=OrderOut, dependencies=[Depends(require_admin)])
def update_status(order_id: int, payload: StatusIn, db: Session = Depends(get_db)):
    if payload.status not in VALID_STATUSES: raise HTTPException(400, "Unsupported order status")
    item = db.get(Order, order_id)
    if not item: raise HTTPException(404, "Order not found")
    item.status = payload.status; db.commit(); db.refresh(item); return item
