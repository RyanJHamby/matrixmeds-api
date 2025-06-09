from typing import List, Dict
import uuid
from datetime import datetime
from app.db.dynamo import db
from app.models.schemas import InteractionCreate, InteractionResponse

class InteractionService:
    @staticmethod
    async def check_interactions(medications: List[str]) -> List[InteractionResponse]:
        interactions = []
        # Check each pair of medications
        for i in range(len(medications)):
            for j in range(i + 1, len(medications)):
                med1, med2 = sorted([medications[i], medications[j]])
                key = {
                    "medication1": med1,
                    "medication2": med2
                }
                
                # Query DynamoDB for interaction
                result = await db.query(
                    "medication1 = :med1 AND medication2 = :med2",
                    {":med1": med1, ":med2": med2}
                )
                
                if result:
                    interactions.extend([
                        InteractionResponse(
                            id=item["id"],
                            medication1=item["medication1"],
                            medication2=item["medication2"],
                            severity=item["severity"],
                            description=item["description"],
                            created_at=item["created_at"],
                            updated_at=item["updated_at"]
                        )
                        for item in result
                    ])
        
        return interactions

    @staticmethod
    async def create_interaction(interaction: InteractionCreate) -> InteractionResponse:
        interaction_dict = interaction.model_dump()
        interaction_dict["id"] = str(uuid.uuid4())
        interaction_dict["created_at"] = datetime.utcnow().isoformat()
        interaction_dict["updated_at"] = datetime.utcnow().isoformat()
        
        # Ensure medications are stored in alphabetical order
        med1, med2 = sorted([interaction_dict["medication1"], interaction_dict["medication2"]])
        interaction_dict["medication1"] = med1
        interaction_dict["medication2"] = med2
        
        await db.put_item(interaction_dict)
        return InteractionResponse(**interaction_dict)

interaction_service = InteractionService() 