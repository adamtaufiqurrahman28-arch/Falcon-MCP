# app/main.py
# Tambahkan import dan mount ini jika belum ada.

from fastapi.staticfiles import StaticFiles

# Setelah app = FastAPI(...)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
