import pytest
from datetime import date
import pandas as pd
from src.parsers.gdelt_parser import GDELTNewsParser, ParserConfig

@pytest.fixture
def parser():
    config = ParserConfig(
        keyword="climate change",
        countries=["US", "AS"],
        language="English"
    )
    return GDELTNewsParser(config)

@pytest.fixture
def mock_articles_df():
    return pd.DataFrame({
        'title': ['Title 1', 'Title 2', 'Title 3'],
        'url': ['url1.com', 'url2.com', 'url3.com'],
        'language': ['English', 'English', 'Spanish']
    })

def test_get_articles(monkeypatch, parser, mock_articles_df):
    def mock_article_search(*args, **kwargs):
        return mock_articles_df
    
    monkeypatch.setattr(parser.gdelt_client, "article_search", mock_article_search)
    
    result = parser.get_articles(date(2024, 1, 1))
    assert len(result) == 2  # Only English articles
    assert all(result['language'] == 'English')

def test_get_articles_empty_result(monkeypatch, parser):
    def mock_article_search(*args, **kwargs):
        return pd.DataFrame()
    
    monkeypatch.setattr(parser.gdelt_client, "article_search", mock_article_search)
    
    result = parser.get_articles(date(2024, 1, 1))
    assert result.empty

def test_get_articles_date_range(monkeypatch, parser, mock_articles_df):
    calls = []
    
    def mock_article_search(filters):
        calls.append(filters)
        return mock_articles_df
    
    monkeypatch.setattr(parser.gdelt_client, "article_search", mock_article_search)
    
    start = date(2024, 1, 1)
    end = date(2024, 1, 5)
    result = parser.get_articles(start, end)
    
    assert len(calls) == 1  # Verify that article_search was called once
    assert len(result) == 2  # Verify we get filtered English results