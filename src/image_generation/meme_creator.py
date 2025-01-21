from pathlib import Path
from typing import Optional
import logging
import asyncio
import io
from PIL import Image
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)

class ImageGenerationError(Exception):
    """Custom exception for image generation errors."""
    pass

class ImageGenerator:
    """Service for generating images from social media posts using Stable Diffusion."""
    
    def __init__(
        self, 
        api_token: str,
        model_id: str = "stabilityai/stable-diffusion-3.5-large-turbo",
        base_prompt: str = """
        Generate a humorous and engaging meme-style image that captures 
        the essence of this social media post. Include:
        - Modern meme aesthetic
        - Vibrant, eye-catching colors
        - Clear focal point
        - Simple, impactful composition
        - Suitable for social media sharing
        Based on this post: 
        """
    ):
        """
        Initialize the ImageGenerator with HuggingFace API token.
        
        Args:
            api_token (str): HuggingFace API token
            model_id (str): Model identifier for image generation
            base_prompt (str): Base prompt template for image generation
            
        Raises:
            ValueError: If api_token is empty or None
        """
        if not api_token:
            raise ValueError("API token cannot be empty or None")
            
        self.client = InferenceClient(
            model=model_id,
            token=api_token
        )
        self.base_prompt = base_prompt
        
    def _construct_prompt(self, post_text: str) -> str:
        """
        Construct the full prompt for image generation.
        
        Args:
            post_text: The social media post text to base the image on
            
        Returns:
            Complete prompt for the image generation model
        """
        return f"{self.base_prompt}\n\"{post_text}\""
    
    async def generate_image(
        self,
        post_text: str,
        save_path: Optional[Path] = None
    ) -> Image.Image:
        """
        Generate an image based on a social media post.
        
        Args:
            post_text: The social media post to generate an image for
            save_path: Optional path to save the generated image. If None, image is only returned
            
        Returns:
            PIL.Image: Generated image
            
        Raises:
            ImageGenerationError: If image generation fails
        """
        try:
            prompt = self._construct_prompt(post_text)
            logger.info(f"Generating image for post: {post_text[:50]}...")
            
            # Run the synchronous image generation in a thread pool
            image = await asyncio.get_event_loop().run_in_executor(
                None,
                self.client.text_to_image,
                prompt
            )
            
            if save_path:
                save_path.parent.mkdir(exist_ok=True, parents=True)
                image.save(save_path, format='PNG')
                logger.info(f"Saved generated image to {save_path}")
                
            return image
                
        except Exception as e:
            error_msg = f"Failed to generate image: {str(e)}"
            logger.error(error_msg)
            raise ImageGenerationError(error_msg) from e
            
    async def generate_image_bytes(self, post_text: str) -> bytes:
        """
        Generate an image and return it as bytes for direct transfer.
        
        Args:
            post_text: The social media post to generate an image for
            
        Returns:
            bytes: Generated image as bytes in PNG format
            
        Raises:
            ImageGenerationError: If image generation fails
        """
        try:
            image = await self.generate_image(post_text)
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
            
        except Exception as e:
            error_msg = f"Failed to convert image to bytes: {str(e)}"
            logger.error(error_msg)
            raise ImageGenerationError(error_msg) from e

async def main():
    """Example usage of the ImageGenerator class."""
    generator = ImageGenerator(api_token="insert_your_huggingface_api_token")
    
    test_post = """Mother's Day Wish: 'Dear Earth, please stop melting and healing, 
    COVID-19 could use a break. Love, Moms everywhere. SMH, y'all parasites fr.'"""
    
    # Example 1: Generate and save image
    image = await generator.generate_image(
        test_post,
        save_path=Path("../../data/images/test_image.png")
    )
    
    # Example 2: Generate image bytes for direct transfer
    image_bytes = await generator.generate_image_bytes(test_post)
    
if __name__ == "__main__":
    asyncio.run(main())

#TODO
#Max requests total reached on image generation inference (3). Wait up to one minute before being able to process more Diffusion requests.
#Implemt calling another endpoint for image generation to avoid exceeding the limit
#Delete text from image