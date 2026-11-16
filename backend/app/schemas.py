from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
class ProductIn(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    category: str = "other"
    description: str = ""
    price_rub: int = Field(default=0, ge=0)
    image_url: str | None = None
    options: str = "{}"
    is_active: bool = True
class ProductOut(ProductIn):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
class OrderIn(BaseModel):
    customer_name: str = Field(min_length=1, max_length=180)
    contact: str = Field(min_length=3, max_length=180)
    address: str = ""
    product_name: str = ""
    variant: str = ""
    quantity: int = Field(default=1, ge=1, le=1000)
    comment: str = ""
    total_rub: int = Field(default=0, ge=0)
class OrderOut(BaseModel):
    id: int
    customer_name: str
    contact: str
    address: str
    product_name: str
    variant: str
    quantity: int
    comment: str
    total_rub: int
    status: str
    receipt_url: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
class StatusIn(BaseModel):
    status: str
