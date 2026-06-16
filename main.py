from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
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
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )

@app.get("/api/companies/{query_string}")
async def get_company(query_string: str, db: Session = Depends(get_db)):
    """
    API Endpoint: Fetches company records by matching either an exact CIN 
    or performing a case-insensitive search on the Company Name.
    """
    try:
        search_term = f"%{query_string}%"
        
        company = db.query(models.Company).filter(
            or_(
                models.Company.CIN == query_string.upper(),
                models.Company.Company_Name.ilike(search_term)
            )
        ).first()
        
        if not company:
            raise HTTPException(
                status_code=404, 
                detail="No company matching that query string could be found."
            )
            
        return company
        
    except Exception as e:
        # Catch connection dropouts or unexpected structural exceptions
        raise HTTPException(
            status_code=500, 
            detail=f"Internal Database Exception: {str(e)}"
        )
