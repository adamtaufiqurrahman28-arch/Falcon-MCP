# Integrated Seraphim BlueTeam Document Summary

File ini sudah menggabungkan fitur Document Summary ke UI Seraphim BlueTeam.

## Copy files

```text
app/web/templates.py
app/services/document_service.py
app/services/document_context.py
app/api/document_routes.py
```

## Update app/main.py

```python
from app.api.document_routes import router as document_router
app.include_router(document_router)
```

## Install dependency

```powershell
pip install python-docx pypdf
```

## Logo

Pastikan file logo ada di:

```text
app/static/img/seraphim-blueteam-logo.png
```

dan `app/main.py` punya static mount:

```python
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="app/static"), name="static")
```
