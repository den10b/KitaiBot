import asyncio
import concurrent.futures
from dataclasses import dataclass
from typing import Callable, Any

import requests
from bs4 import BeautifulSoup
from requests import Response

from database.models import News
from tgbot.services.translator import news_translator


@dataclass
class NewsInfo:
    title: str
    direct_link: str
    preview_image_link: str
    description: str

    def __str__(self):
        return f"news_title={self.title}\n" \
               f"news_direct_link={self.direct_link}\n" \
               f"news_preview_image_link={self.preview_image_link}\n" \
               f"news_description={self.description}"


async def run_in_blocking_io(func: Callable, *args) -> Any:
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, func, *args)


async def get(url: str) -> Response:
    return await run_in_blocking_io(requests.get, url)


async def get_news_data(response: Response, base_url: str) -> list[NewsInfo]:
    soup = BeautifulSoup(response.text, "lxml")
    items = soup.find("div", class_="largeTitle").find_all("article", class_="js-article-item articleItem")
    news = []
    for item in items:
        news_title = item.find("div", class_="textDiv").find("a").get("title").strip()
        news_direct_link = base_url + item.find("a").get("href").strip()
        news_preview_image_link = item.find("img").get("data-src").strip()
        news_description = item.find("div", class_="textDiv").find("p").get_text().replace("...", "").strip()
        news.append(
            NewsInfo(
                title=news_title,
                direct_link=news_direct_link,
                preview_image_link=news_preview_image_link,
                description=news_description
            )
        )
    return news


async def get_news(key_words: list[str], category: str = 'latest-news'):
    domain = "https://www.investing.com"
    base_url_to_news = f"{domain}/news"
    url = f"{base_url_to_news}/{category}"
    response = await get(url)
    news = await get_news_data(response, domain)
    translated_news = await news_translator(news)
    for word in key_words:
        for new in translated_news:
            is_in_db = News.objects.filter(title=new.title).first()
            if is_in_db:
                continue
            if word in new.title or word in new.description:
                News(
                    word=word,
                    title=new.title,
                    direct_link=new.direct_link,
                    preview_image_link=new.preview_image_link,
                    description=new.description
                ).save()
