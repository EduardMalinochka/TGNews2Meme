import asyncio
from datetime import date
from typing import List, Dict

from parsers.gdelt_parser import GDELTNewsParser, ParserConfig
from llm.tweet_generator import TweetGenerator
from tg_bot.sending_bot import TelegramBot
from utils.load_config import load_config
from image_generation.meme_creator import ImageGenerator
from memory.news_storage import NewsStorage

import logging
logger = logging.getLogger(__name__)

async def process_articles(
    articles: List[Dict], 
    tweet_generator: TweetGenerator, 
    image_generator: ImageGenerator,
    telegram_bot: TelegramBot,
    news_storage: NewsStorage
):
    """Process articles and send them to Telegram with generated images."""
    for article in articles:
        try:
            # Check if title is new
            success, similar_titles = await news_storage.add_title(article['title'])
            if not success:
                logger.info(f"Skipping duplicate title: {article['title']}")
                continue

            # Generate tweet
            tweet = await tweet_generator.generate_tweet(article['title'])
            
            # Generate image
            image_bytes = await image_generator.generate_image_bytes(tweet)
            
            # Send to Telegram
            success = await telegram_bot.send_message(
                text=f"{tweet}\n\n{article['url']}",
                image_bytes=image_bytes
            )
            
            if not success:
                logger.error(f"Failed to send message for article: {article['title']}")
                
        except Exception as e:
            logger.error(f"Error processing article '{article['title']}': {str(e)}")
            continue

async def main():
    try:
        # Load configuration
        config = load_config('/Users/eduardlukutin/Desktop/tg_commenter/.env')
        
        # Initialize components
        parser_config = ParserConfig(
            keyword="climate change",
            countries=["US", "GB", "CA"],
            language="English"
        )
        
        parser = GDELTNewsParser(parser_config)
        tweet_generator = TweetGenerator(config["HUGGINGFACE_LLM_TOKEN"])
        image_generator = ImageGenerator(config["HUGGINGFACE_IMAGE_TOKEN"])
        telegram_bot = TelegramBot(config["BOT_TOKEN"], config["CHAT_ID"])
        
        # Initialize NewsStorage
        news_storage = NewsStorage(
            supabase_url=config["SUPABASE_URL"],
            supabase_key=config["SUPABASE_KEY"]
        )
        await news_storage.initialize_database()  # Initialize database schema
        
        # Use fixed dates for article search
        start_date = date(2020, 5, 10)
        end_date = date(2020, 5, 11)
        
        # Get articles for the specified date range
        articles_df = parser.get_articles(start_date, end_date)
        
        if articles_df.empty:
            print(f"No articles found between {start_date} and {end_date}")
            return
            
        # Take the top 5 articles
        top_articles = articles_df.head(5).to_dict('records')
        
        # Process articles with duplicate checking
        await process_articles(
            top_articles, 
            tweet_generator, 
            image_generator,
            telegram_bot,
            news_storage  # Pass storage instance
        )
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())