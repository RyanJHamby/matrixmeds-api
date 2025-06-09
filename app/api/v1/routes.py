from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import (
    InteractionCreate,
    InteractionResponse,
    InteractionCheckRequest,
    InteractionCheckResponse
)
from app.services.interactions import interaction_service
from app.auth.cognito import auth

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