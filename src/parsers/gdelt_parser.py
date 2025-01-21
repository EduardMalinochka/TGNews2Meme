from dataclasses import dataclass
from datetime import date
from typing import List, Optional
import pandas as pd
from gdeltdoc import GdeltDoc, Filters

@dataclass
class ParserConfig:
    """Configuration for the news parser."""
    keyword: str
    countries: List[str]
    language: str = "English"

class GDELTNewsParser:
    """Parser for fetching news articles from GDELT."""
    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.gdelt_client = GdeltDoc()

    def get_articles(
        self,
        start_date: date,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """
        Fetch articles from GDELT and filter by language.
        Returns filtered DataFrame.
        """
        end_date = end_date or start_date
        
        filters = Filters(
            keyword=self.config.keyword,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            country=self.config.countries
        )
        
        articles_df = self.gdelt_client.article_search(filters)
        
        if not articles_df.empty:
            articles_df = articles_df[
                articles_df['language'] == self.config.language
            ]
        
        return articles_df