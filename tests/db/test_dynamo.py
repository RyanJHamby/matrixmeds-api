import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from botocore.exceptions import ClientError
from app.db.dynamo import DynamoDB

@pytest.fixture
def mock_dynamodb():
    with patch("boto3.resource") as mock:
        mock_table = MagicMock()
        mock_table.get_item = AsyncMock()
        mock_table.put_item = AsyncMock()
        mock_table.update_item = AsyncMock()
        mock_table.delete_item = AsyncMock()
        mock_table.query = AsyncMock()
        mock.return_value.Table.return_value = mock_table
        yield mock_table

@pytest.mark.asyncio
async def test_get_item(mock_dynamodb):
    mock_dynamodb.get_item.return_value = {"Item": {"id": "123", "name": "test"}}
    db = DynamoDB()
    
    result = await db.get_item({"id": "123"})
    assert result == {"id": "123", "name": "test"}
    mock_dynamodb.get_item.assert_called_once_with(Key={"id": "123"})

@pytest.mark.asyncio
async def test_get_item_not_found(mock_dynamodb):
    mock_dynamodb.get_item.return_value = {}
    db = DynamoDB()
    
    result = await db.get_item({"id": "123"})
    assert result is None

@pytest.mark.asyncio
async def test_get_item_error(mock_dynamodb):
    mock_dynamodb.get_item.side_effect = ClientError(
        {"Error": {"Code": "ResourceNotFoundException"}},
        "get_item"
    )
    db = DynamoDB()
    
    with pytest.raises(Exception) as exc_info:
        await db.get_item({"id": "123"})
    assert "Error getting item" in str(exc_info.value)

@pytest.mark.asyncio
async def test_put_item(mock_dynamodb):
    item = {"id": "123", "name": "test"}
    db = DynamoDB()
    
    result = await db.put_item(item)
    assert result == item
    mock_dynamodb.put_item.assert_called_once_with(Item=item)

@pytest.mark.asyncio
async def test_put_item_error(mock_dynamodb):
    mock_dynamodb.put_item.side_effect = ClientError(
        {"Error": {"Code": "ValidationException"}},
        "put_item"
    )
    db = DynamoDB()
    
    with pytest.raises(Exception) as exc_info:
        await db.put_item({"id": "123"})
    assert "Error putting item" in str(exc_info.value)

@pytest.mark.asyncio
async def test_update_item(mock_dynamodb):
    mock_dynamodb.update_item.return_value = {
        "Attributes": {"id": "123", "name": "updated"}
    }
    db = DynamoDB()
    
    result = await db.update_item(
        {"id": "123"},
        "SET #n = :name",
        {":name": "updated"}
    )
    assert result == {"id": "123", "name": "updated"}
    mock_dynamodb.update_item.assert_called_once_with(
        Key={"id": "123"},
        UpdateExpression="SET #n = :name",
        ExpressionAttributeValues={":name": "updated"},
        ReturnValues="ALL_NEW"
    )

@pytest.mark.asyncio
async def test_update_item_error(mock_dynamodb):
    mock_dynamodb.update_item.side_effect = ClientError(
        {"Error": {"Code": "ValidationException"}},
        "update_item"
    )
    db = DynamoDB()
    
    with pytest.raises(Exception) as exc_info:
        await db.update_item(
            {"id": "123"},
            "SET #n = :name",
            {":name": "updated"}
        )
    assert "Error updating item" in str(exc_info.value)

@pytest.mark.asyncio
async def test_delete_item(mock_dynamodb):
    db = DynamoDB()
    
    await db.delete_item({"id": "123"})
    mock_dynamodb.delete_item.assert_called_once_with(Key={"id": "123"})

@pytest.mark.asyncio
async def test_delete_item_error(mock_dynamodb):
    mock_dynamodb.delete_item.side_effect = ClientError(
        {"Error": {"Code": "ResourceNotFoundException"}},
        "delete_item"
    )
    db = DynamoDB()
    
    with pytest.raises(Exception) as exc_info:
        await db.delete_item({"id": "123"})
    assert "Error deleting item" in str(exc_info.value)

@pytest.mark.asyncio
async def test_query(mock_dynamodb):
    mock_dynamodb.query.return_value = {
        "Items": [{"id": "123", "name": "test"}]
    }
    db = DynamoDB()
    
    result = await db.query(
        "id = :id",
        {":id": "123"}
    )
    assert result == [{"id": "123", "name": "test"}]
    mock_dynamodb.query.assert_called_once_with(
        KeyConditionExpression="id = :id",
        ExpressionAttributeValues={":id": "123"}
    )

@pytest.mark.asyncio
async def test_query_empty(mock_dynamodb):
    mock_dynamodb.query.return_value = {"Items": []}
    db = DynamoDB()
    
    result = await db.query(
        "id = :id",
        {":id": "123"}
    )
    assert result == []

@pytest.mark.asyncio
async def test_query_error(mock_dynamodb):
    mock_dynamodb.query.side_effect = ClientError(
        {"Error": {"Code": "ValidationException"}},
        "query"
    )
    db = DynamoDB()
    
    with pytest.raises(Exception) as exc_info:
        await db.query(
            "id = :id",
            {":id": "123"}
        )
    assert "Error querying items" in str(exc_info.value) 