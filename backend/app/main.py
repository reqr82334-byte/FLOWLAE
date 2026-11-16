from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .config import settings
from .routers import products, orders
Base.metadata.create_all(bind=engine)
app = FastAPI(title="FLOWLAE API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=False, allow_methods=["GET","POST","PATCH","DELETE"], allow_headers=["Content-Type","X-Admin-Key"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
@app.get("/health")
def health(): return {"status":"ok","service":"flowlae-api"}
