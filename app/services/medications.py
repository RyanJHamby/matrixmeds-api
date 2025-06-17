from typing import Optional
from datetime import datetime, UTC
from app.db.dynamo import DynamoDB
from app.models.schemas import MedicationCreate, MedicationResponse
from app.config import settings

class MedicationService:
    def __init__(self, db: DynamoDB):
        self.db = db
        self.table_name = settings.MEDICATIONS_TABLE

    async def list_medications(
        self,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[list[MedicationResponse], int, bool]:
        """List medications with search and pagination"""
        # Calculate offset
        offset = (page - 1) * limit

        # Build query
        query_params = {
            "TableName": self.table_name,
            "Limit": limit + 1  # Get one extra to check if there are more
        }

        if search:
            # Use GSI for search if available, otherwise filter results
            query_params["FilterExpression"] = "contains(#name, :search) OR contains(#generic_name, :search)"
            query_params["ExpressionAttributeNames"] = {
                "#name": "name",
                "#generic_name": "generic_name"
            }
            query_params["ExpressionAttributeValues"] = {
                ":search": search.lower()
            }

        # Execute query
        response = await self.db.query(**query_params)
        items = response.get("Items", [])

        # Check if there are more results
        has_more = len(items) > limit
        if has_more:
            items = items[:-1]  # Remove the extra item

        # Convert to response models
        medications = [
            MedicationResponse(
                id=item["id"],
                name=item["name"],
                generic_name=item["generic_name"],
                description=item["description"],
                dosage_forms=item["dosage_forms"],
                active_ingredients=item["active_ingredients"],
                warnings=item.get("warnings", []),
                side_effects=item.get("side_effects", []),
                manufacturer=item["manufacturer"],
                category=item["category"],
                created_at=item["created_at"],
                updated_at=item["updated_at"]
            )
            for item in items
        ]

        # Get total count if needed
        total = await self._get_total_count(search) if page == 1 else None

        return medications, total, has_more

    async def get_medication(self, medication_id: str) -> Optional[MedicationResponse]:
        """Get medication by ID"""
        response = await self.db.get_item(
            TableName=self.table_name,
            Key={"id": medication_id}
        )

        item = response.get("Item")
        if not item:
            return None

        return MedicationResponse(
            id=item["id"],
            name=item["name"],
            generic_name=item["generic_name"],
            description=item["description"],
            dosage_forms=item["dosage_forms"],
            active_ingredients=item["active_ingredients"],
            warnings=item.get("warnings", []),
            side_effects=item.get("side_effects", []),
            manufacturer=item["manufacturer"],
            category=item["category"],
            created_at=item["created_at"],
            updated_at=item["updated_at"]
        )

    async def _get_total_count(self, search: Optional[str] = None) -> int:
        """Get total count of medications"""
        query_params = {
            "TableName": self.table_name,
            "Select": "COUNT"
        }

        if search:
            query_params["FilterExpression"] = "contains(#name, :search) OR contains(#generic_name, :search)"
            query_params["ExpressionAttributeNames"] = {
                "#name": "name",
                "#generic_name": "generic_name"
            }
            query_params["ExpressionAttributeValues"] = {
                ":search": search.lower()
            }

        response = await self.db.query(**query_params)
        return response.get("Count", 0) 