from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models
from database import engine, get_db

app = FastAPI(title="Company Enrichment System Engine")

# Create database tables automatically if they don't exist yet
models.Base.metadata.create_all(bind=engine)

# Mount static asset pipelines (CSS, JS, Images) safely
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 web view templater engine context reference
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """
    Renders the central system analytics dashboard UI interface.
    """
    # Explicitly passing request as both a keyword parameter and context key
    # completely satisfies both older and newer FastAPI/Starlette dependencies.
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )

@app.get("/api/companies/{cin}")
async def get_company_by_cin(cin: str, db: Session = Depends(get_db)):
    """
    API Endpoint: Fetches detailed profile metrics for a specific target company via its unique CIN.
    """
    company = db.query(models.Company).filter(models.Company.CIN == cin.upper()).first()
    if not company:
        raise HTTPException(status_code=404, detail="Requested Corporate Identifier (CIN) not found inside database registries.")
    return company
