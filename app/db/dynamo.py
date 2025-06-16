import boto3
from botocore.exceptions import ClientError
from typing import Dict, List, Optional
from app.config import settings

class DynamoDB:
    def __init__(self):
        kwargs = {
            "region_name": settings.AWS_REGION,
        }
        if settings.ENVIRONMENT == "test":
            kwargs["endpoint_url"] = settings.DYNAMODB_ENDPOINT
            kwargs["aws_access_key_id"] = "dummy"
            kwargs["aws_secret_access_key"] = "dummy"
            
        self.dynamodb = boto3.resource("dynamodb", **kwargs)
        self.table = self.dynamodb.Table(settings.DYNAMODB_TABLE)

    async def get_item(self, key: Dict) -> Optional[Dict]:
        try:
            response = await self.table.get_item(Key=key)
            return response.get("Item")
        except ClientError as e:
            raise Exception(f"Error getting item: {str(e)}")

    async def put_item(self, item: Dict) -> Dict:
        try:
            await self.table.put_item(Item=item)
            return item
        except ClientError as e:
            raise Exception(f"Error putting item: {str(e)}")

    async def update_item(
        self,
        key: Dict,
        update_expression: str,
        expression_values: Dict
    ) -> Dict:
        try:
            response = await self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues="ALL_NEW"
            )
            return response.get("Attributes", {})
        except ClientError as e:
            raise Exception(f"Error updating item: {str(e)}")

    async def delete_item(self, key: Dict) -> None:
        try:
            await self.table.delete_item(Key=key)
        except ClientError as e:
            raise Exception(f"Error deleting item: {str(e)}")

    async def query(
        self,
        key_condition_expression: str,
        expression_values: Dict
    ) -> List[Dict]:
        try:
            response = await self.table.query(
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_values
            )
            return response.get("Items", [])
        except ClientError as e:
            raise Exception(f"Error querying items: {str(e)}")

db = DynamoDB() 