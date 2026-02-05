import random
import feedparser
import requests
from typing import Optional
from .base_strategy import BaseStrategy


class NewsStrategy(BaseStrategy):
    def generate_prompt(self) -> Optional[str]:
        try:
            config = self.config.get('config', {})
            rss_urls = config.get('rss_urls', [])
            
            if not rss_urls:
                return None
            
            rss_url = random.choice(rss_urls)
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                return None
            
            entry = random.choice(feed.entries[:10])
            news_title = entry.get('title', '')
            
            max_length = config.get('max_news_length', 200)
            if len(news_title) > max_length:
                news_title = news_title[:max_length] + '...'
            
            prompt_template = config.get('prompt_template', '用一句话概括这条新闻的核心内容：{news_title}')
            return prompt_template.format(news_title=news_title)
        
        except Exception as e:
            return None
