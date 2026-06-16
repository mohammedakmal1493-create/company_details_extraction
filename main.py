from fastapi import FastAPI, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
import models
from database import engine, get_db

app = FastAPI(title="Company Enrichment Engine")

# Sync schema state definitions across your active connection pooler
models.Base.metadata.create_all(bind=engine)

# Mount asset directory safely
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/companies")
async def get_initial_companies(db: Session = Depends(get_db)):
    """Fetches the top 50 rows to initialize the sidebar layout view."""
    companies = db.query(models.Company).limit(50).all()
    return companies

@app.get("/search")
async def search_companies(q: str = Query(...), db: Session = Depends(get_db)):
    """Handles real-time queries matching text patterns across CIN or Name."""
    search_pattern = f"%{q}%"
    companies = db.query(models.Company).filter(
        or_(
            models.Company.CIN.ilike(search_pattern),
            models.Company.Company_Name.ilike(search_pattern)
        )
    ).limit(100).all()
    return companies

@app.get("/company/{id}")
async def get_company_details(id: str, db: Session = Depends(get_db)):
    """Fetches details for a single record row using its unique string ID (CIN)."""
    company = db.query(models.Company).filter(models.Company.CIN == id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company profile data row missing.")
    return company

@app.get("/pipeline/trigger")
@app.post("/pipeline/trigger")
async def trigger_pipeline():
    """Placeholder endpoint for matching your pipeline click interaction triggers."""
    return {"message": "Enrichment pipeline dispatch process initialized for the target batch!"}
