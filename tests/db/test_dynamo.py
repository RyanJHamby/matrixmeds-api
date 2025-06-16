import pytest
from unittest.mock import AsyncMock, patch
from app.db.dynamo import DynamoDB
from botocore.exceptions import ClientError

@pytest.fixture
def mock_table():
    with patch("boto3.resource") as mock_resource:
        mock_table = AsyncMock()
        mock_resource.return_value.Table.return_value = mock_table
        yield mock_table

@pytest.mark.asyncio
async def test_get_item(mock_table):
    mock_table.get_item.return_value = {
        "Item": {
            "id": "123",
            "medication1": "Drug A",
            "medication2": "Drug B"
        }
    }
    db = DynamoDB()
    result = await db.get_item({"id": "123"})
    assert result["id"] == "123"
    assert result["medication1"] == "Drug A"
    assert result["medication2"] == "Drug B"

@pytest.mark.asyncio
async def test_get_item_not_found(mock_table):
    mock_table.get_item.return_value = {}
    db = DynamoDB()
    result = await db.get_item({"id": "123"})
    assert result is None

@pytest.mark.asyncio
async def test_get_item_error(mock_table):
    mock_table.get_item.side_effect = ClientError(
        {"Error": {"Code": "ResourceNotFoundException"}},
        "GetItem"
    )
    db = DynamoDB()
    with pytest.raises(Exception) as exc_info:
        await db.get_item({"id": "123"})
    assert "Error getting item" in str(exc_info.value)

@pytest.mark.asyncio
async def test_put_item(mock_table):
    item = {
        "id": "123",
        "medication1": "Drug A",
        "medication2": "Drug B"
    }
    mock_table.put_item.return_value = {"Item": item}
    db = DynamoDB()
    result = await db.put_item(item)
    assert result == item

@pytest.mark.asyncio
async def test_put_item_error(mock_table):
    mock_table.put_item.side_effect = ClientError(
        {"Error": {"Code": "ValidationException"}},
        "PutItem"
    )
    db = DynamoDB()
    with pytest.raises(Exception) as exc_info:
        await db.put_item({"id": "123"})
    assert "Error putting item" in str(exc_info.value)

@pytest.mark.asyncio
async def test_update_item(mock_table):
    mock_table.update_item.return_value = {
        "Attributes": {
            "id": "123",
            "medication1": "Drug A",
            "medication2": "Drug B"
        }
    }
    db = DynamoDB()
    result = await db.update_item(
        {"id": "123"},
        "SET medication1 = :med1",
        {":med1": "Drug A"}
    )
    assert result["id"] == "123"
    assert result["medication1"] == "Drug A"

@pytest.mark.asyncio
async def test_update_item_error(mock_table):
    mock_table.update_item.side_effect = ClientError(
        {"Error": {"Code": "ValidationException"}},
        "UpdateItem"
    )
    db = DynamoDB()
    with pytest.raises(Exception) as exc_info:
        await db.update_item(
            {"id": "123"},
            "SET medication1 = :med1",
            {":med1": "Drug A"}
        )
    assert "Error updating item" in str(exc_info.value)

@pytest.mark.asyncio
async def test_delete_item(mock_table):
    mock_table.delete_item.return_value = {}
    db = DynamoDB()
    await db.delete_item({"id": "123"})
    mock_table.delete_item.assert_called_once()

@pytest.mark.asyncio
async def test_delete_item_error(mock_table):
    mock_table.delete_item.side_effect = ClientError(
        {"Error": {"Code": "ValidationException"}},
        "DeleteItem"
    )
    db = DynamoDB()
    with pytest.raises(Exception) as exc_info:
        await db.delete_item({"id": "123"})
    assert "Error deleting item" in str(exc_info.value)

@pytest.mark.asyncio
async def test_query(mock_table):
    mock_table.query.return_value = {
        "Items": [
            {
                "id": "123",
                "medication1": "Drug A",
                "medication2": "Drug B"
            }
        ]
    }
    db = DynamoDB()
    result = await db.query(
        "medication1 = :med1",
        {":med1": "Drug A"}
    )
    assert len(result) == 1
    assert result[0]["id"] == "123"

@pytest.mark.asyncio
async def test_query_empty(mock_table):
    mock_table.query.return_value = {"Items": []}
    db = DynamoDB()
    result = await db.query(
        "medication1 = :med1",
        {":med1": "Drug A"}
    )
    assert len(result) == 0

@pytest.mark.asyncio
async def test_query_error(mock_table):
    mock_table.query.side_effect = ClientError(
        {"Error": {"Code": "ValidationException"}},
        "Query"
    )
    db = DynamoDB()
    with pytest.raises(Exception) as exc_info:
        await db.query(
            "medication1 = :med1",
            {":med1": "Drug A"}
        )
    assert "Error querying items" in str(exc_info.value) 