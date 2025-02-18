import re
import logging
from typing import List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from supabase import Client, create_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SimilarTitle:
    """Data class to represent a similar title match."""
    id: int
    title: str
    similarity: float
    created_at: datetime

class TitleNormalizer:
    """Handles title normalization logic."""
    
    @staticmethod
    def normalize(title: str) -> str:
        """
        Normalize a title for comparison.
        
        Args:
            title: Raw title string
            
        Returns:
            Normalized title string
        """
        if not isinstance(title, str):
            raise ValueError("Title must be a string")
            
        title_lower = title.lower()
        title_no_punct = re.sub(r'[^a-z0-9\s]+', '', title_lower)
        return re.sub(r'\s+', ' ', title_no_punct).strip()

class NewsStorageError(Exception):
    """Custom exception for NewsStorage-related errors."""
    pass

class NewsStorage:
    """Handles storage and retrieval of news titles with similarity checking."""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """
        Initialize NewsStorage with Supabase credentials.
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
        """
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL and key are required")
            
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.normalizer = TitleNormalizer()

    async def initialize_database(self) -> None:
        """
        Initialize the database schema and required extensions.
        """
        sql = """
        CREATE EXTENSION IF NOT EXISTS pg_trgm;

        CREATE TABLE IF NOT EXISTS news_titles (
            id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
            title TEXT NOT NULL,
            normalized_title TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, now()) NOT NULL
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_news_titles_normalized_title
            ON news_titles (normalized_title);

        -- ... (other indexes remain the same)

        CREATE OR REPLACE FUNCTION search_news_titles(
            search_text TEXT,
            min_similarity DOUBLE PRECISION DEFAULT 0.3
        )
        RETURNS TABLE (
            id BIGINT,
            title TEXT,
            similarity DOUBLE PRECISION,
            created_at TIMESTAMP WITH TIME ZONE
        )
        LANGUAGE plpgsql
        SECURITY DEFINER
        AS $$
        BEGIN
            RETURN QUERY
            SELECT
                nt.id,
                nt.title,
                CAST(similarity(nt.normalized_title, search_text) AS DOUBLE PRECISION) as similarity,
                nt.created_at
            FROM news_titles nt
            WHERE similarity(nt.normalized_title, search_text) > min_similarity
            ORDER BY similarity DESC;
        END;
        $$;
        """

        try:
            self.supabase.rpc('exec_sql', {'sql_string': sql}).execute()
            logger.info("Database initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize database: {str(e)}"
            logger.error(error_msg)
            raise NewsStorageError(error_msg)

    async def find_similar_titles(
        self, 
        normalized_title: str,
        min_similarity: float = 0.5
    ) -> List[SimilarTitle]:
        """
        Find titles similar to the given normalized title.
        """
        try:
            # Remove await from execute()
            response = self.supabase.rpc(
                'search_news_titles',
                {
                    'search_text': normalized_title,
                    'min_similarity': min_similarity
                }
            ).execute()
            
            return [
                SimilarTitle(
                    id=item['id'],
                    title=item['title'],
                    similarity=item['similarity'],
                    created_at=datetime.fromisoformat(item['created_at'])
                )
                for item in response.data
            ]
        except Exception as e:
            error_msg = f"Error finding similar titles: {str(e)}"
            logger.error(error_msg)
            raise NewsStorageError(error_msg)

    async def add_title(
        self, 
        title: str, 
        min_similarity: float = 0.5
    ) -> Tuple[bool, Optional[List[SimilarTitle]]]:
        """
        Add a new title if no similar titles exist.
        """
        try:
            normalized = self.normalizer.normalize(title)
            
            # Check for similar titles
            similar_titles = await self.find_similar_titles(normalized, min_similarity)
            if similar_titles:
                logger.info(f"Similar titles found for: {title}")
                return False, similar_titles

            # Add new title - remove await
            response = self.supabase.table("news_titles").insert({
                "title": title,
                "normalized_title": normalized,
            }).execute()

            if response.data:
                logger.info(f"Successfully added new title: {title}")
                return True, None
            else:
                raise NewsStorageError(f"Unexpected status code: {response.status_code}")

        except Exception as e:
            error_msg = f"Error adding title: {str(e)}"
            logger.error(error_msg)
            raise NewsStorageError(error_msg)

class NewsProcessor:
    """Handles the processing of news titles."""
    
    def __init__(self, storage: NewsStorage):
        """
        Initialize NewsProcessor with a storage backend.
        
        Args:
            storage: NewsStorage instance
        """
        self.storage = storage

    async def process_title(self, title: str) -> Tuple[bool, str]:
        """
        Process a news title - check for duplicates and store if unique.
        
        Args:
            title: News title to process
            
        Returns:
            Tuple of (success boolean, status message)
        """
        try:
            success, similar_titles = await self.storage.add_title(title)
            
            if success:
                return True, f"Successfully processed new title: {title}"
            else:
                similar_titles_str = "\n".join(
                    f"- {t.title} (similarity: {t.similarity:.2f})"
                    for t in similar_titles
                )
                return False, f"Similar titles found:\n{similar_titles_str}"
                
        except NewsStorageError as e:
            return False, f"Failed to process title: {str(e)}"