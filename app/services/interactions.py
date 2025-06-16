from typing import List, Dict
import uuid
from datetime import datetime, UTC
from app.db.dynamo import db
from app.models.schemas import InteractionCreate, InteractionResponse

class InteractionService:
    async def check_interactions(self, medications: List[str]) -> List[InteractionResponse]:
        interactions = []
        for i in range(len(medications)):
            for j in range(i + 1, len(medications)):
                med1, med2 = sorted([medications[i], medications[j]])
                result = await db.query(
                    "medication1 = :med1 AND medication2 = :med2",
                    {":med1": med1, ":med2": med2}
                )
                if result:
                    interactions.extend([
                        InteractionResponse(**item)
                        for item in result
                    ])
        return interactions

    async def create_interaction(self, interaction: InteractionCreate) -> InteractionResponse:
        # Sort medications to ensure consistent ordering
        med1, med2 = sorted([interaction.medication1, interaction.medication2])
        
        interaction_dict = interaction.model_dump()
        interaction_dict["medication1"] = med1
        interaction_dict["medication2"] = med2
        interaction_dict["id"] = str(uuid.uuid4())
        interaction_dict["created_at"] = datetime.now(UTC).isoformat()
        interaction_dict["updated_at"] = datetime.now(UTC).isoformat()
        
        await db.put_item(interaction_dict)
        return InteractionResponse(**interaction_dict)

interaction_service = InteractionService() 