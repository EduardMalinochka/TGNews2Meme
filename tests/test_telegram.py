import pytest
from unittest.mock import patch, AsyncMock
from pathlib import Path
from src.tg_bot.sending_bot import TelegramBot

class AsyncContextManagerMock:
    """A better implementation of an async context manager mock."""
    def __init__(self, mock_file_content=b"mock_file_content"):
        self.mock_file_content = mock_file_content

    async def __aenter__(self):
        return self.mock_file_content

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.fixture
def telegram_bot():
    """Fixture for creating a TelegramBot instance with mocked dependencies."""
    with patch("src.tg_bot.sending_bot.Bot") as mock_bot_class:
        # Create a single mock instance to track all calls
        mock_bot_instance = AsyncMock()
        mock_bot_instance.send_message = AsyncMock()
        mock_bot_instance.send_photo = AsyncMock()
        mock_bot_class.return_value = mock_bot_instance
        
        bot = TelegramBot(token="test_token", chat_id="test_chat_id")
        # Store the mock instance for easier assertions
        bot._mock = mock_bot_instance
        yield bot

class TestTelegramBot:
    """Group all related tests in a class for better organization."""
    
    @pytest.mark.asyncio
    async def test_send_message_text_only(self, telegram_bot):
        """Test sending a text-only message."""
        await telegram_bot.send_message("Test message")
        
        telegram_bot._mock.send_message.assert_called_once_with(
            chat_id="test_chat_id",
            text="Test message"
        )

    @pytest.mark.asyncio
    async def test_send_message_with_image(self, telegram_bot):
        """Test sending a message with an image."""
        mock_file_content = b"mock_image_content"
        
        # Mock both the file open and Path.exists()
        with patch("builtins.open", return_value=AsyncContextManagerMock(mock_file_content)), \
             patch.object(Path, "exists", return_value=True):  # Add this line
            await telegram_bot.send_message(
                "Message with image",
                image_path="path/to/image.jpg"
            )

            telegram_bot._mock.send_photo.assert_called_once_with(
                chat_id="test_chat_id",
                photo=mock_file_content,
                caption="Message with image"
            )

    @pytest.mark.asyncio
    async def test_send_message_with_nonexistent_image(self, telegram_bot):
        """Test sending a message with a nonexistent image."""
        with patch.object(Path, "exists", return_value=False), \
             pytest.raises(FileNotFoundError, match="Image not found at.*"):
            await telegram_bot.send_message(
                "Message with image",
                image_path="nonexistent.jpg"
            )

    @pytest.mark.asyncio
    async def test_send_message_none_text_raises_error(self, telegram_bot):
        """Test that sending None as text raises TypeError."""
        with pytest.raises(TypeError, match="Text cannot be None"):
            await telegram_bot.send_message(None)

    @pytest.mark.asyncio
    async def test_send_message_empty_text(self, telegram_bot):
        """Test sending an empty string as message."""
        await telegram_bot.send_message("")
        
        telegram_bot._mock.send_message.assert_called_once_with(
            chat_id="test_chat_id",
            text=""
        )