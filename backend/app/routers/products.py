from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import require_admin
from ..models import Product
from ..schemas import ProductIn, ProductOut
router = APIRouter()
@router.get("", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.is_active.is_(True)).order_by(Product.id.desc()).all()
@router.post("", response_model=ProductOut, dependencies=[Depends(require_admin)])
def create_product(payload: ProductIn, db: Session = Depends(get_db)):
    item = Product(**payload.model_dump()); db.add(item); db.commit(); db.refresh(item); return item
@router.patch("/{product_id}", response_model=ProductOut, dependencies=[Depends(require_admin)])
def update_product(product_id: int, payload: ProductIn, db: Session = Depends(get_db)):
    item = db.get(Product, product_id)
    if not item: raise HTTPException(404, "Product not found")
    for key, value in payload.model_dump().items(): setattr(item, key, value)
    db.commit(); db.refresh(item); return item
@router.delete("/{product_id}", dependencies=[Depends(require_admin)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    item = db.get(Product, product_id)
    if not item: raise HTTPException(404, "Product not found")
    db.delete(item); db.commit(); return {"ok": True}
@router.patch("/{product_id}/visibility", dependencies=[Depends(require_admin)])
def set_visibility(product_id: int, active: bool, db: Session = Depends(get_db)):
    item = db.get(Product, product_id)
    if not item: raise HTTPException(404, "Product not found")
    item.is_active = active; db.commit(); return {"id": item.id, "is_active": item.is_active}
