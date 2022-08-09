import asyncio

import aiohttp
from bs4 import BeautifulSoup

from tgbot.services.news_parser import NewsInfo, get_news


async def translate(text: str, language_to: str, language_from: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://translate.google.com/m?tl={language_to}&sl={language_from}&q={text}') as \
                response:
            result = await response.text()
            source = BeautifulSoup(result, "lxml")

            return source.find("div", attrs={"class": "result-container"}).text


async def news_translator(news: list[NewsInfo]):
    translated_news = []
    for new in news:
        title = await translate(new.title, "ru", "en")
        description = await translate(new.description, "ru", "en")
        translated_news.append(
            NewsInfo(
                title=title,
                direct_link=new.direct_link,
                preview_image_link=new.preview_image_link,
                description=description
            )
        )

    return translated_news
