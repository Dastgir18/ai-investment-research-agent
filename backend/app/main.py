from fastapi import FastAPI , HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.agents.pipeline import run_pipeline
from app.agents.investment_pipeline import run_investment_pipeline
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

app = FastAPI(
    title="IntelAgent API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────
# REQUEST MODELS — what user sends in
# ─────────────────────────────────────
class ResearchRequest(BaseModel):
    company: str

# ─────────────────────────────────────
# RESPONSE MODELS — what API sends back
# ─────────────────────────────────────
class MarketResponse(BaseModel):
    company: str
    report: str
    status: str

class InvestmentRequest(BaseModel):
    company: str
    recommendation: Optional[str]
    risk_score: Optional[int]
    time_horizon: Optional[str]
    executive_summary: Optional[str]
    bull_case: Optional[str]
    bear_case: Optional[str]
    key_risks: Optional[str]
    financial_highlights: Optional[str]
    reasoning: Optional[str]
    status: str

# ─────────────────────────────────────
# BASIC ENDPOINTS
# ─────────────────────────────────────

@app.get("/")
async def root():
    return {
        "message": "Welcome to IntelAgent",
        "version": "0.1.0",
        "endpoints": 
        {
            "/research": "POST - Run market research pipeline for a company",
            "/invest": "POST - Run investment research pipeline for a company",
            "docs":"GET - API documentation"
        }
}

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "0.1.0",
        "message": "IntelAgent API is running"
    }

# ─────────────────────────────────────
# MARKET RESEARCH ENDPOINT
# ─────────────────────────────────────

@app.post("/research", response_model=MarketResponse)
async def research(request: ResearchRequest):
    company = request.company.strip()
    if not company:
        raise HTTPException(
            status_code=400, 
            detail="Company name cannot be empty"
            )
    if len(company) < 2:
        raise HTTPException(
            status_code=400, 
            detail="Company name is to short."
            )
    print(f"\nAPI - Market research for Company: {company}")


    
    result = run_pipeline(request.company)

    if result["status"] !="complete":
        raise HTTPException(
            status_code=500, 
            detail=f"Pipeline failed: {result.get('error', 'Unknown error')}"
            )
    
    return MarketResponse(
        company=result["company"],
        report=result["report"],
        status=result["status"]
    )

# ─────────────────────────────────────
# INVESTMENT RESEARCH ENDPOINT
# ─────────────────────────────────────



@app.post("/invest")
async def invest(request: ResearchRequest):
    company = request.company.strip()
    if not company:
        raise HTTPException(
            status_code=400, 
            detail="Company name cannot be empty"
            )
    if len(company) < 2:
        raise HTTPException(
            status_code=400, 
            detail="Company name is to short."
            )
    print(f"\nAPI - Investment research for Company: {company}")


    result = run_investment_pipeline(company)

    if result["status"] !="complete":
        raise HTTPException(
            status_code=500, 
            detail=f"Investment Pipeline failed: {result.get['error']}"
            )
    
    memo = result["memo"]

    if memo is None:
        raise HTTPException(
            status_code=500, 
            detail="Investment memo generation failed."
            )
    
    return InvestmentRequest(
        company=result["company"],
        recommendation=memo.get("recommendation"),
        risk_score=memo.get("risk_score"),
        time_horizon=memo.get("time_horizon"),
        executive_summary=memo.get("executive_summary"),
        bull_case=memo.get("bull_case"),
        bear_case=memo.get("bear_case"),
        key_risks=memo.get("key_risks"),
        financial_highlights=memo.get("financial_highlights"),
        reasoning=memo.get("reasoning"),
        status=result["status"]

    )

    