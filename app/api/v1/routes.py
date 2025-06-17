from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import (
    InteractionCreate,
    InteractionResponse,
    InteractionCheckRequest,
    InteractionCheckResponse,
    MedicationListResponse,
    MedicationResponse
)
from app.services.interactions import interaction_service
from app.auth.cognito import auth
from app.services.medications import MedicationService

router = APIRouter()

@router.post("/interactions/check", response_model=InteractionCheckResponse)
async def check_interactions(
    request: InteractionCheckRequest,
    _: dict = Depends(auth.validate_token)
):
    interactions = await interaction_service.check_interactions(request.medications)
    return InteractionCheckResponse(
        interactions=interactions,
        has_interactions=len(interactions) > 0
    )

@router.post("/interactions", response_model=InteractionResponse)
async def create_interaction(
    interaction: InteractionCreate,
    _: dict = Depends(auth.validate_token)
):
    return await interaction_service.create_interaction(interaction)

@router.get("/medications", response_model=MedicationListResponse)
async def list_medications(
    search: str = None,
    page: int = 1,
    limit: int = 50,
    medication_service: MedicationService = Depends(get_medication_service)
):
    """List medications with search and pagination"""
    medications, total, has_more = await medication_service.list_medications(
        search=search,
        page=page,
        limit=limit
    )
    
    return MedicationListResponse(
        items=medications,
        total=total or len(medications),
        page=page,
        limit=limit,
        has_more=has_more
    )

@router.get("/medications/{medication_id}", response_model=MedicationResponse)
async def get_medication(
    medication_id: str,
    medication_service: MedicationService = Depends(get_medication_service)
):
    """Get detailed medication info"""
    medication = await medication_service.get_medication(medication_id)
    if not medication:
        raise HTTPException(
            status_code=404,
            detail=f"Medication with ID {medication_id} not found"
        )
    return medication 