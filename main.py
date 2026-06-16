from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from sqlalchemy.orm import Session
from database import get_db, engine
import models
from pipeline import run_pipeline

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Company Enrichment Engine")
templates = Jinja2Templates(directory="templates")

# Open A:\full_dev_intern\main.py and update line 17 to this exact keyword syntax:

@app.get("/")
async def serve_dashboard(request: Request):
    # Pass context explicitly as a named keyword argument
    return templates.TemplateResponse(
        name="index.html", 
        context={"request": request}
    )

@app.get("/companies")
def get_companies(db: Session = Depends(get_db)):
    # Restricts page loads to first 100 entries to protect memory
    return db.query(models.Company).order_by(models.Company.id.asc()).limit(100).all()

@app.get("/company/{id}")
def get_company_by_id(id: int, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company record not found")
    return company

@app.get("/search")
def search_companies(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    results = db.query(models.Company).filter(
        (models.Company.Company_Name.like(f"%{q}%")) | 
        (models.Company.CIN.like(f"%{q}%"))
    ).limit(50).all()
    return results

@app.post("/pipeline/trigger")
def trigger_pipeline(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_pipeline)
    return {"message": "Enrichment started for the top 100 companies."}
