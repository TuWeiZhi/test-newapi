import random
import requests
from bs4 import BeautifulSoup
from typing import Optional
from .base_strategy import BaseStrategy


class WebpageStrategy(BaseStrategy):
    def generate_prompt(self) -> Optional[str]:
        try:
            config = self.config.get('config', {})
            urls = config.get('urls', [])
            
            if not urls:
                return None
            
            url = random.choice(urls)
            timeout = config.get('timeout', 10)
            
            response = requests.get(url, timeout=timeout, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            page_title = soup.title.string if soup.title else url
            
            prompt_template = config.get('prompt_template', '总结这个网页标题的主题：{page_title}')
            return prompt_template.format(page_title=page_title)
        
        except Exception as e:
            return None
