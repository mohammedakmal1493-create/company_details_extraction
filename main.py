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
    """
    Renders the central split-panel system analytics dashboard UI interface.
    Uses modern keyword arguments to prevent template engine signature crashes.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )

@app.get("/companies")
async def get_initial_companies(db: Session = Depends(get_db)):
    """Fetches the top 50 rows to initialize the sidebar layout view on load."""
    companies = db.query(models.Company).limit(50).all()
    return companies

@app.get("/search")
async def search_companies(q: str = Query(...), db: Session = Depends(get_db)):
    """Handles real-time text matching queries across CIN or Name values."""
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
    """Fetches full specifications for a single company row using its unique CIN string."""
    company = db.query(models.Company).filter(models.Company.CIN == id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company profile data row missing.")
    return company

@app.post("/pipeline/trigger")
async def trigger_pipeline():
    """Endpoint hook for your bulk background enrichment dispatch actions."""
    return {"message": "Enrichment pipeline dispatch process initialized for the target batch!"}
