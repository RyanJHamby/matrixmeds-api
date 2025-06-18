import pytest
from unittest.mock import AsyncMock, patch
from app.db.dynamo import DynamoDB
from botocore.exceptions import ClientError

@pytest.fixture
def mock_table():
    """Mock DynamoDB table"""
    mock = AsyncMock()
    with patch("boto3.resource") as mock_resource:
        mock_resource.return_value.Table.return_value = mock
        yield mock

@pytest.mark.asyncio
async def test_get_item_success(mock_table):
    """Test successful get_item operation"""
    mock_table.get_item.return_value = {
        "Item": {
            "id": "123",
            "name": "Test Item"
        }
    }
    db = DynamoDB()
    result = await db.get_item({"id": "123"})
    assert result["id"] == "123"
    assert result["name"] == "Test Item"
    mock_table.get_item.assert_called_once_with(Key={"id": "123"})

@pytest.mark.asyncio
async def test_get_item_not_found(mock_table):
    """Test get_item when item doesn't exist"""
    mock_table.get_item.return_value = {}
    db = DynamoDB()
    result = await db.get_item({"id": "999"})
    assert result is None
    mock_table.get_item.assert_called_once_with(Key={"id": "999"})

@pytest.mark.asyncio
async def test_get_item_error(mock_table):
    """Test get_item error handling"""
    mock_table.get_item.side_effect = ClientError(
        {"Error": {"Code": "ResourceNotFoundException", "Message": "Table not found"}},
        "GetItem"
    )
    db = DynamoDB()
    with pytest.raises(Exception, match="Error getting item"):
        await db.get_item({"id": "123"})

@pytest.mark.asyncio
async def test_put_item_success(mock_table):
    """Test successful put_item operation"""
    item = {"id": "123", "name": "Test Item"}
    mock_table.put_item.return_value = None
    db = DynamoDB()
    result = await db.put_item(item)
    assert result == item
    mock_table.put_item.assert_called_once_with(Item=item)

@pytest.mark.asyncio
async def test_put_item_error(mock_table):
    """Test put_item error handling"""
    mock_table.put_item.side_effect = ClientError(
        {"Error": {"Code": "ValidationException", "Message": "Invalid item"}},
        "PutItem"
    )
    db = DynamoDB()
    with pytest.raises(Exception, match="Error putting item"):
        await db.put_item({"id": "123"})

@pytest.mark.asyncio
async def test_update_item_success(mock_table):
    """Test successful update_item operation"""
    mock_table.update_item.return_value = {
        "Attributes": {
            "id": "123",
            "name": "Updated Item",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    }
    db = DynamoDB()
    result = await db.update_item(
        {"id": "123"},
        "SET #name = :name, #updated_at = :updated_at",
        {":name": "Updated Item", ":updated_at": "2024-01-01T00:00:00Z"}
    )
    assert result["name"] == "Updated Item"
    mock_table.update_item.assert_called_once_with(
        Key={"id": "123"},
        UpdateExpression="SET #name = :name, #updated_at = :updated_at",
        ExpressionAttributeValues={":name": "Updated Item", ":updated_at": "2024-01-01T00:00:00Z"},
        ReturnValues="ALL_NEW"
    )

@pytest.mark.asyncio
async def test_update_item_error(mock_table):
    """Test update_item error handling"""
    mock_table.update_item.side_effect = ClientError(
        {"Error": {"Code": "ConditionalCheckFailedException", "Message": "Condition not met"}},
        "UpdateItem"
    )
    db = DynamoDB()
    with pytest.raises(Exception, match="Error updating item"):
        await db.update_item(
            {"id": "123"},
            "SET #name = :name",
            {":name": "Updated Item"}
        )

@pytest.mark.asyncio
async def test_delete_item_success(mock_table):
    """Test successful delete_item operation"""
    mock_table.delete_item.return_value = None
    db = DynamoDB()
    await db.delete_item({"id": "123"})
    mock_table.delete_item.assert_called_once_with(Key={"id": "123"})

@pytest.mark.asyncio
async def test_delete_item_error(mock_table):
    """Test delete_item error handling"""
    mock_table.delete_item.side_effect = ClientError(
        {"Error": {"Code": "ResourceNotFoundException", "Message": "Table not found"}},
        "DeleteItem"
    )
    db = DynamoDB()
    with pytest.raises(Exception, match="Error deleting item"):
        await db.delete_item({"id": "123"})

@pytest.mark.asyncio
async def test_query_success(mock_table):
    """Test successful query operation"""
    mock_table.query.return_value = {
        "Items": [
            {
                "id": "123",
                "medication1": "Drug A",
                "medication2": "Drug B"
            }
        ],
        "Count": 1
    }
    db = DynamoDB()
    result = await db.query(
        key_condition_expression="medication1 = :med1",
        expression_values={":med1": "Drug A"}
    )
    assert result["Items"][0]["id"] == "123"
    assert result["Count"] == 1
    mock_table.query.assert_called_once_with(
        KeyConditionExpression="medication1 = :med1",
        ExpressionAttributeValues={":med1": "Drug A"}
    )

@pytest.mark.asyncio
async def test_query_with_filter(mock_table):
    """Test query with filter expression"""
    mock_table.query.return_value = {
        "Items": [
            {
                "id": "123",
                "medication1": "Drug A",
                "medication2": "Drug B"
            }
        ],
        "Count": 1
    }
    db = DynamoDB()
    result = await db.query(
        key_condition_expression="medication1 = :med1",
        expression_values={":med1": "Drug A"},
        filter_expression="medication2 = :med2",
        expression_attribute_names={"#med2": "medication2"},
        limit=10
    )
    assert result["Items"][0]["id"] == "123"
    mock_table.query.assert_called_once_with(
        KeyConditionExpression="medication1 = :med1",
        ExpressionAttributeValues={":med1": "Drug A"},
        FilterExpression="medication2 = :med2",
        ExpressionAttributeNames={"#med2": "medication2"},
        Limit=10
    )

@pytest.mark.asyncio
async def test_query_empty(mock_table):
    """Test query with no results"""
    mock_table.query.return_value = {"Items": [], "Count": 0}
    db = DynamoDB()
    result = await db.query(
        key_condition_expression="medication1 = :med1",
        expression_values={":med1": "Drug A"}
    )
    assert len(result["Items"]) == 0
    assert result["Count"] == 0

@pytest.mark.asyncio
async def test_query_error(mock_table):
    """Test query error handling"""
    mock_table.query.side_effect = ClientError(
        {"Error": {"Code": "ValidationException", "Message": "Invalid expression"}},
        "Query"
    )
    db = DynamoDB()
    with pytest.raises(Exception, match="Error querying items"):
        await db.query(
            key_condition_expression="invalid expression",
            expression_values={":med1": "Drug A"}
        )

@pytest.mark.asyncio
async def test_query_with_select(mock_table):
    """Test query with select parameter"""
    mock_table.query.return_value = {"Count": 5}
    db = DynamoDB()
    result = await db.query(select="COUNT")
    assert result["Count"] == 5
    mock_table.query.assert_called_once_with(Select="COUNT") 