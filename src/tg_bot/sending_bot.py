from typing import Optional
from pathlib import Path
import logging
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

class TelegramBot:
    """A class to handle Telegram message sending operations."""
    
    def __init__(self, token: str, chat_id: str):
        """
        Initialize the TelegramBot.
        
        Args:
            token (str): Telegram bot API token
            chat_id (str): Target chat ID for messages
        
        Raises:
            ValueError: If token or chat_id is empty
        """
        if not token or not chat_id:
            raise ValueError("Both token and chat_id must be provided")
            
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def send_message(
            self, 
            text: str, 
            image_bytes: Optional[bytes] = None,
            image_path: Optional[str | Path] = None
        ) -> bool:
            """
            Send a message to Telegram, with an image from bytes or file.
            
            Args:
                text (str): The message text or image caption
                image_bytes (Optional[bytes]): Image as bytes
                image_path (Optional[str | Path]): Path to image file
                
            Returns:
                bool: True if message was sent successfully, False otherwise
                
            Raises:
                TypeError: If text is None
                FileNotFoundError: If image_path is provided but file doesn't exist
                ValueError: If both image_bytes and image_path are provided
            """
            if text is None:
                raise TypeError("Text cannot be None")
                
            if image_bytes and image_path:
                raise ValueError("Cannot provide both image_bytes and image_path")
                
            try:
                if image_bytes:
                    await self.bot.send_photo(
                        chat_id=self.chat_id, 
                        photo=image_bytes, 
                        caption=text
                    )
                elif image_path:
                    image_path = Path(image_path)
                    if not image_path.exists():
                        raise FileNotFoundError(f"Image not found at {image_path}")
                        
                    async with open(image_path, 'rb') as image_file:
                        await self.bot.send_photo(
                            chat_id=self.chat_id, 
                            photo=image_file, 
                            caption=text
                        )
                else:
                    await self.bot.send_message(
                        chat_id=self.chat_id, 
                        text=text
                    )
                return True
                
            except TelegramError as e:
                logger.error(f"Failed to send message to Telegram: {str(e)}")
                return False
