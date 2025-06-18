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
        offset = (page - 1) * limit
        
        # Build query parameters
        query_kwargs = {}
        if search:
            query_kwargs["filter_expression"] = "contains(#name, :search) OR contains(#generic_name, :search)"
            query_kwargs["expression_attribute_names"] = {
                "#name": "name",
                "#generic_name": "generic_name"
            }
            query_kwargs["expression_attribute_values"] = {
                ":search": search.lower()
            }
        if limit is not None:
            query_kwargs["limit"] = limit + 1
            
        response = await self.db.query(**query_kwargs)
        items = response.get("Items", [])
        has_more = len(items) > limit
        if has_more:
            items = items[:-1]
            
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
        total = await self._get_total_count(search) if page == 1 else None
        return medications, total, has_more

    async def get_medication(self, medication_id: str) -> Optional[MedicationResponse]:
        response = await self.db.get_item({"id": medication_id})
        if not response:
            return None
            
        return MedicationResponse(
            id=response["id"],
            name=response["name"],
            generic_name=response["generic_name"],
            description=response["description"],
            dosage_forms=response["dosage_forms"],
            active_ingredients=response["active_ingredients"],
            warnings=response.get("warnings", []),
            side_effects=response.get("side_effects", []),
            manufacturer=response["manufacturer"],
            category=response["category"],
            created_at=response["created_at"],
            updated_at=response["updated_at"]
        )

    async def _get_total_count(self, search: Optional[str] = None) -> int:
        query_kwargs = {"select": "COUNT"}
        if search:
            query_kwargs["filter_expression"] = "contains(#name, :search) OR contains(#generic_name, :search)"
            query_kwargs["expression_attribute_names"] = {
                "#name": "name",
                "#generic_name": "generic_name"
            }
            query_kwargs["expression_attribute_values"] = {
                ":search": search.lower()
            }
        response = await self.db.query(**query_kwargs)
        return response.get("Count", 0) 