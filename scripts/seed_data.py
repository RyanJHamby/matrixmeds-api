import asyncio
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.interactions import interaction_service
from app.models.schemas import InteractionCreate

async def seed_interactions():
    interactions = [
        InteractionCreate(
            medication1="Aspirin",
            medication2="Warfarin",
            severity="High",
            description="Increased risk of bleeding when taken together"
        ),
        InteractionCreate(
            medication1="Lisinopril",
            medication2="Ibuprofen",
            severity="Moderate",
            description="May reduce blood pressure-lowering effects"
        ),
        InteractionCreate(
            medication1="Simvastatin",
            medication2="Grapefruit",
            severity="High",
            description="Grapefruit can increase simvastatin levels in blood"
        ),
        InteractionCreate(
            medication1="Metformin",
            medication2="Contrast Dye",
            severity="High",
            description="Risk of kidney damage when used with contrast dye"
        ),
        InteractionCreate(
            medication1="Warfarin",
            medication2="Vitamin K",
            severity="Moderate",
            description="Vitamin K can reduce warfarin's effectiveness"
        )
    ]
    
    for interaction in interactions:
        try:
            await interaction_service.create_interaction(interaction)
            print(f"Created interaction: {interaction.medication1} - {interaction.medication2}")
        except Exception as e:
            print(f"Error creating interaction: {str(e)}")

if __name__ == "__main__":
    asyncio.run(seed_interactions()) 