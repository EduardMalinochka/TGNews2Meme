from typing import Optional, List
import textwrap
import asyncio
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate


class TweetGenerator:
    """
    A class to generate Twitter-style posts from news headlines using Mistral LLM.
    """
    
    def __init__(self, api_token: str, timeout: int = 30):
        """
        Initialize the TweetGenerator with HuggingFace API token.
        
        Args:
            api_token (str): HuggingFace API token
            timeout (int): Timeout in seconds for LLM calls (default: 30)
            
        Raises:
            ValueError: If api_token is empty or None
        """
        if not api_token:
            raise ValueError("API token cannot be empty or None")
            
        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.3",
            huggingfacehub_api_token=api_token
        )
        self.timeout = timeout
        
        self.prompt_template = PromptTemplate(
            input_variables=["article_title"],
            template="""
            Generate a humorous tweet-style comment (under 280 characters) for the given news headline. The tone should be witty, relatable, and use casual online language. Incorporate acronyms like 'fr', 'smh', 'wtf', and terms like 'parasites', 'fools', 'poverty mindset' if appropriate. Refer to the examples below for inspiration:

            HEADLINE: Scientists Discover New Super-Earth 12 Light Years Away
            Comment: New Super-Earth discovered, and the first thing humans think is 'can we move there and ruin that one too?' Parasites fr.

            HEADLINE: Global Economy Faces Unprecedented Challenges
            Comment: Unprecedented challenges = ‘we broke it but can’t fix it.’ Classic human vibes. Let’s just reboot 2025 already, smh.

            HEADLINE: Elon Musk Announces Plan to Colonize Mars
            Comment: Bruh, we can't even fix potholes on Earth, but yeah, Mars is def the move. Priorities on point, Elon. Parasitic energy.

            HEADLINE: Local Man Breaks World Record for Eating Hot Dogs
            Comment: Breaking news: man eats 72 hot dogs. Somewhere, a cardiologist just fainted. FR, why tho? WTF is this timeline?

            HEADLINE: AI Takes Over Routine Office Tasks
            Comment: AI’s out here doing spreadsheets while we scroll memes at work. Parasites fr, but hey, efficiency is efficiency!

            HEADLINE: Global Warming Causes Unusual Weather Patterns
            Comment: Weather be like, ‘you want snow or hurricanes?’ Humans: ‘yes.’ Smh, climate change fr playing us like Sims.

            HEADLINE: Billionaires Compete to Build Space Hotels
            Comment: Space hotels? Bro, we just want affordable rent on Earth. Meanwhile Bezos and Musk out here playing Monopoly with the galaxy. WTF.

            Now, based on the above style and tone, comment on the following headline:

            HEADLINE: {article_title}
            Comment:
            """
        )
    
    async def generate_tweet(self, headline: str, max_attempts: int = 3) -> Optional[str]:
        """
        Generate a Twitter-style post from a news headline.
        
        Args:
            headline (str): The news headline to base the tweet on
            max_attempts (int): Maximum number of retry attempts if generation fails
            
        Returns:
            Optional[str]: Generated tweet text, or None if generation fails
            
        Raises:
            ValueError: If headline is empty or None
        """
        if not headline:
            raise ValueError("Headline cannot be empty or None")
            
        for attempt in range(max_attempts):
            try:
                prompt = self.prompt_template.format(article_title=headline)
                print(f"Attempt {attempt + 1}/{max_attempts} for headline: {headline}")
                
                async with asyncio.timeout(self.timeout):
                    response = await self.llm.ainvoke(prompt)
                
                if not response:
                    print("Received empty response from LLM")
                    continue
                    
                tweet = textwrap.shorten(
                    response.strip('\'" \t\n\r\v\f'), 
                    width=280, 
                    placeholder="..."
                )
                
                # Basic validation of generated tweet
                if len(tweet) < 10:
                    print(f"Generated tweet too short: {tweet}")
                    continue
                    
                return tweet
                
            except asyncio.TimeoutError:
                print(f"Attempt {attempt + 1} timed out after {self.timeout} seconds")
                await asyncio.sleep(1)  # Add delay between retries
                continue
            except Exception as e:
                print(f"Error during attempt {attempt + 1}: {str(e)}")
                await asyncio.sleep(1)  # Add delay between retries
                continue
                
        print(f"Failed to generate tweet for headline after {max_attempts} attempts")
        return None

    async def generate_batch(self, headlines: List[str]) -> List[Optional[str]]:
        """
        Generate tweets for multiple headlines concurrently.
        
        Args:
            headlines (List[str]): List of headlines to generate tweets for
            
        Returns:
            List[Optional[str]]: List of generated tweets (None for failed generations)
            
        Raises:
            ValueError: If headlines list is empty
        """
        if not headlines:
            raise ValueError("Headlines list cannot be empty")
            
        tasks = [self.generate_tweet(headline) for headline in headlines]
        return await asyncio.gather(*tasks)

    def update_prompt_template(self, new_template: str) -> None:
        """
        Update the prompt template used for generation.
        
        Args:
            new_template (str): New prompt template to use
            
        Raises:
            ValueError: If new_template is empty or None
        """
        if not new_template:
            raise ValueError("New template cannot be empty or None")
            
        self.prompt_template = PromptTemplate(
            input_variables=["article_title"],
            template=new_template
        )


async def main():
    """Example usage of the TweetGenerator class."""
    # Replace with your API token
    api_token = "insert_your_huggingface_api_token"
    
    # Create generator with custom timeout
    tweet_generator = TweetGenerator(api_token, timeout=45)
    
    # Single headline example
    headline = "Scientists Discover New Super-Earth 12 Light Years Away"
    tweet = await tweet_generator.generate_tweet(headline)
    if tweet:
        print(f"\nSingle headline result:")
        print(f"Headline: {headline}")
        print(f"Tweet: {tweet}")
    
    # Batch processing example
    headlines = [
        "Global Renewable Energy Usage Hits Record High",
        "New AI Model Can Predict Weather Patterns with 95% Accuracy",
        "Scientists Develop Revolutionary Cancer Treatment"
    ]
    
    print("\nBatch processing results:")
    tweets = await tweet_generator.generate_batch(headlines)
    for headline, tweet in zip(headlines, tweets):
        if tweet:
            print(f"\nHeadline: {headline}")
            print(f"Tweet: {tweet}")


if __name__ == "__main__":
    asyncio.run(main())