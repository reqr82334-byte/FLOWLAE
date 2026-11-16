import asyncio, os
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
load_dotenv()
TOKEN=os.getenv("BOT_TOKEN","")
ADMIN_ID=int(os.getenv("ADMIN_TELEGRAM_ID","0"))
API=os.getenv("API_BASE_URL","http://127.0.0.1:8000").rstrip("/")
KEY=os.getenv("ADMIN_API_KEY","")
dp=Dispatcher()
def allowed(m): return bool(ADMIN_ID and m.from_user and m.from_user.id==ADMIN_ID)
async def api(method,path,payload=None):
    async with aiohttp.ClientSession(headers={"X-Admin-Key":KEY}) as s:
        async with s.request(method,API+path,json=payload) as r:
            data=await r.json()
            if r.status>=400: raise RuntimeError(str(data))
            return data
@dp.message(Command("start"))
async def start(m:Message):
    if not allowed(m): return await m.answer("Доступ только для администратора.")
    await m.answer("FLOWLAE ADMIN\n/orders — заказы\n/products — товары\n/add_product Название | категория | цена | описание\n/edit_product ID | Название | категория | цена | описание\n/hide_product ID\n/show_product ID\n/delete_product ID\n/status ID | awaiting_payment\nСтатусы: awaiting_payment, paid, purchased, at_warehouse, shipped, delivered")
@dp.message(Command("orders"))
async def orders(m:Message):
    if not allowed(m): return
    try:
        rows=await api("GET","/api/orders")
        await m.answer("\n\n".join(f"#{o['id']} {o['customer_name']} · {o['contact']}\n{o['product_name']} · {o['total_rub']} ₽ · {o['status']}" for o in rows[:20]) or "Заказов пока нет.")
    except Exception as e: await m.answer(f"API error: {e}")
@dp.message(Command("products"))
async def products(m:Message):
    if not allowed(m): return
    try:
        rows=await api("GET","/api/products")
        await m.answer("\n".join(f"#{p['id']} {p['name']} · {p['price_rub']} ₽" for p in rows) or "Активных товаров нет.")
    except Exception as e: await m.answer(f"API error: {e}")
def fields(text,n):
    p=[x.strip() for x in text.split("|",n-1)]
    if len(p)!=n: raise ValueError("Неверное количество полей")
    return p
@dp.message(Command("add_product"))
async def add(m:Message):
    if not allowed(m): return
    try:
        name,cat,price,desc=fields(m.text.partition(" ")[2],4)
        p=await api("POST","/api/products",{"name":name,"category":cat,"price_rub":int(price),"description":desc})
        await m.answer(f"Добавлен товар #{p['id']}: {p['name']}")
    except Exception as e: await m.answer(f"Формат: /add_product Название | категория | цена | описание\n{e}")
@dp.message(Command("edit_product"))
async def edit(m:Message):
    if not allowed(m): return
    try:
        pid,name,cat,price,desc=fields(m.text.partition(" ")[2],5)
        p=await api("PATCH",f"/api/products/{int(pid)}",{"name":name,"category":cat,"price_rub":int(price),"description":desc,"is_active":True})
        await m.answer(f"Обновлён товар #{p['id']}")
    except Exception as e: await m.answer(f"Формат: /edit_product ID | Название | категория | цена | описание\n{e}")
async def visibility(m,active):
    if not allowed(m): return
    try:
        pid=int(m.text.partition(" ")[2])
        r=await api("PATCH",f"/api/products/{pid}/visibility?active={str(active).lower()}")
        await m.answer(f"Товар #{pid}: {'виден' if r['is_active'] else 'скрыт'}")
    except Exception as e: await m.answer(f"Ошибка: {e}")
@dp.message(Command("hide_product"))
async def hide(m): await visibility(m,False)
@dp.message(Command("show_product"))
async def show(m): await visibility(m,True)
@dp.message(Command("delete_product"))
async def delete(m):
    if not allowed(m): return
    try:
        pid=int(m.text.partition(" ")[2]); await api("DELETE",f"/api/products/{pid}"); await m.answer(f"Удалён товар #{pid}")
    except Exception as e: await m.answer(f"Ошибка: {e}")
@dp.message(Command("status"))
async def status(m):
    if not allowed(m): return
    try:
        pid,value=fields(m.text.partition(" ")[2],2)
        o=await api("PATCH",f"/api/orders/{int(pid)}/status",{"status":value})
        await m.answer(f"Заказ #{o['id']}: {o['status']}")
    except Exception as e: await m.answer(f"Формат: /status ID | статус\n{e}")
async def main():
    if not TOKEN or not ADMIN_ID or not KEY: raise RuntimeError("Заполните BOT_TOKEN, ADMIN_TELEGRAM_ID и ADMIN_API_KEY в bot/.env")
    await dp.start_polling(Bot(TOKEN))
if __name__=="__main__": asyncio.run(main())
