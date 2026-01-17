from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, desc
from .db import SessionLocal, engine, Base
from .models import Record

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# 起動時にテーブル作成（最小運用ならこれでOK）
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    with SessionLocal() as db:
        records = db.execute(select(Record).order_by(desc(Record.created_at)).limit(10)).scalars().all()
    return templates.TemplateResponse("index.html", {"request": request, "records": records})

@app.get("/all", response_class=HTMLResponse)
def all_records(request: Request):
    with SessionLocal() as db:
        records = db.execute(select(Record).order_by(desc(Record.created_at))).scalars().all()
    return templates.TemplateResponse("all.html", {"request": request, "records": records})

@app.post("/records")
def create_record(
    note: str = Form(...),
    mood: str | None = Form(None),
):
    note = note.strip()
    if not note:
        return RedirectResponse(url="/?error=empty", status_code=303)

    mood_int = None
    if mood and mood.strip():
        try:
            m = int(mood)
            if 1 <= m <= 5:
                mood_int = m
        except ValueError:
            mood_int = None

    with SessionLocal() as db:
        db.add(Record(note=note, mood=mood_int))
        db.commit()

    return RedirectResponse(url="/", status_code=303)
