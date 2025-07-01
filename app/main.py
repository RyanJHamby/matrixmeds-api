from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import router as v1_router
from app.config import settings
from mangum import Mangum

app = FastAPI(
    title="MatrixMeds API",
    description="API for MatrixMeds interaction checking service",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(v1_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

lambda_handler = Mangum(app) 