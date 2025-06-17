from app.services.medications import MedicationService

def get_medication_service(db: DynamoDB = Depends(get_db)) -> MedicationService:
    return MedicationService(db) 