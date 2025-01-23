import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone
from src.memory.news_storage import (
    TitleNormalizer, 
    NewsStorage, 
    NewsProcessor, 
    NewsStorageError,
    SimilarTitle
)

# Fixture for creating a mock Supabase client
@pytest.fixture
def mock_supabase_client():
    client = MagicMock()
    
    # Setup for rpc().execute()
    mock_rpc_instance = MagicMock()
    mock_rpc_instance.execute = AsyncMock()
    client.rpc.return_value = mock_rpc_instance
    
    # Setup for table().insert().execute()
    mock_table_instance = MagicMock()
    mock_insert_instance = MagicMock()
    mock_insert_instance.execute = AsyncMock()
    mock_table_instance.insert.return_value = mock_insert_instance
    client.table.return_value = mock_table_instance
    
    return client

@pytest.fixture
def news_storage(mock_supabase_client):
    with patch('src.memory.news_storage.create_client', return_value=mock_supabase_client):
        return NewsStorage('https://mock.supabase.co', 'mock_key')


# Test TitleNormalizer
def test_title_normalizer():
    normalizer = TitleNormalizer()
    
    # Test basic normalization
    assert normalizer.normalize("Hello, World!") == "hello world"
    
    # Test multiple spaces
    assert normalizer.normalize("  Hello   World  ") == "hello world"
    
    # Test mixed case and punctuation
    assert normalizer.normalize("Breaking NEWS: Big Event!") == "breaking news big event"
    
    # Test invalid input
    with pytest.raises(ValueError):
        normalizer.normalize(None)

@pytest.mark.asyncio
async def test_find_similar_titles(news_storage, mock_supabase_client):
    mock_response = MagicMock()
    mock_response.data = [{'id': 1, 'title': 'Test', 'similarity': 0.8, 'created_at': datetime.now(timezone.utc).isoformat()}]
    
    # Configure execute to return mock response
    mock_supabase_client.rpc.return_value.execute = AsyncMock(return_value=mock_response)
    
    result = await news_storage.find_similar_titles("Test Title")
    assert len(result) == 1

@pytest.mark.asyncio
async def test_add_title_success(news_storage, mock_supabase_client):
    # Mock no similar titles
    news_storage.find_similar_titles = AsyncMock(return_value=[])
    
    # Configure insert response
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_supabase_client.table.return_value.insert.return_value.execute = AsyncMock(return_value=mock_response)
    
    success, _ = await news_storage.add_title("New Title")
    assert success is True


@pytest.mark.asyncio
async def test_add_title_duplicate(news_storage, mock_supabase_client):
    # Setup mock for similar titles
    similar_mock = [
        SimilarTitle(
            id=1, 
            title='Existing Similar Title', 
            similarity=0.5, 
            created_at=datetime.now(timezone.utc)
        )
    ]
    news_storage.find_similar_titles = AsyncMock(return_value=similar_mock)
    
    # Test adding a duplicate title
    success, returned_similar_titles = await news_storage.add_title("Duplicate Title")
    
    assert success is False
    assert returned_similar_titles == similar_mock

@pytest.mark.asyncio
async def test_news_processor(news_storage):
    # Create processor
    processor = NewsProcessor(news_storage)
    
    # Mock add_title to simulate success
    news_storage.add_title = AsyncMock(return_value=(True, None))
    
    # Test processing a new title
    success, message = await processor.process_title("New Title")
    
    assert success is True
    assert "Successfully processed" in message

@pytest.mark.asyncio
async def test_news_processor_duplicate(news_storage):
    # Create processor
    processor = NewsProcessor(news_storage)
    
    # Mock similar titles
    similar_titles = [
        SimilarTitle(
            id=1, 
            title='Similar Title', 
            similarity=0.5, 
            created_at=datetime.now(timezone.utc)
        )
    ]
    
    # Mock add_title to simulate duplicate
    news_storage.add_title = AsyncMock(return_value=(False, similar_titles))
    
    # Test processing a duplicate title
    success, message = await processor.process_title("Duplicate Title")
    
    assert success is False
    assert "Similar titles found" in message

# Error handling test
@pytest.mark.asyncio
async def test_add_title_error(news_storage, mock_supabase_client):
    # Setup to raise an exception
    mock_supabase_client.table.return_value.insert.return_value.execute = AsyncMock(side_effect=Exception("Test Error"))
    
    # Patch the supabase client
    news_storage.supabase = mock_supabase_client
    
    # Test error handling
    with pytest.raises(NewsStorageError):
        await news_storage.add_title("Error Title")