# Tambahkan ke app/main.py

from app.api.document_routes import router as document_router

app.include_router(document_router)
