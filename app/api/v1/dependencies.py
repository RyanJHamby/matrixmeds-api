from fastapi import Depends
from app.db.dynamo import DynamoDB
from app.services.medications import MedicationService

def get_db() -> DynamoDB:
    return DynamoDB()

def get_medication_service(db: DynamoDB = Depends(get_db)) -> MedicationService:
    return MedicationService(db) 