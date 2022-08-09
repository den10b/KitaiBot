import asyncio
from dataclasses import dataclass

import aiohttp
from bs4 import BeautifulSoup

from database.models import GemToBuy


async def get(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()


async def get_page(url) -> BeautifulSoup:
    html = await get(url)
    return BeautifulSoup(html, "lxml")


async def get_stone_info(direct_link_to_stone_page: str, domain_url: str):
    stone_page = (await get_page(direct_link_to_stone_page))
    stone_specification = stone_page.find(
        "div",
        class_="uk-width-1-2@s uk-padding uk-padding-remove-top"
    ).find_all("div", class_="uk-grid-small")
    form: str = stone_specification[2].find_all("div")[-1].get_text().strip()
    image: str = f'{domain_url}{stone_page.find("div", class_="uk-width-1-2@s").find("a").get("href")}'
    size: str = stone_specification[3].find_all("div")[-1].get_text().strip()
    def_gia: str = stone_specification[-1].find_all("div")[-1].get_text().strip()
    price: str = stone_specification[0].find_all(
        "div",
        class_="uk-h2 uk-margin-remove-top"
    )[-1].get_text().replace("$", "").replace(" ", "").strip()
    match form:
        case "R57":
            form = GemToBuy.Form.R57
        case "Cushion":
            form = GemToBuy.Form.CUSHION
        case "Marquise":
            form = GemToBuy.Form.MARQUISE
        case "Oval":
            form = GemToBuy.Form.OVAL
        case "Pear":
            form = GemToBuy.Form.PEAR
    match def_gia:
        case "VS1":
            def_gia = GemToBuy.DefGia.VS1
        case "VVS1":
            def_gia = GemToBuy.DefGia.VVS1
        case "SI1":
            def_gia = GemToBuy.DefGia.SI1
        case "SI2":
            def_gia = GemToBuy.DefGia.SI2
    try:
        gem_to_buy, _ = GemToBuy.objects.get_or_create(
            form=form,
            image=image,
            size=size,
            def_gia=def_gia,
            price=price
        )
        gem_to_buy.save()
    except Exception as e:
        print(e)
        GemToBuy(
            form=form,
            image=image,
            size=size,
            def_gia=def_gia,
            price=price
        ).save()


async def get_stones_data(page: BeautifulSoup, domain_url: str):
    products = page.find("div", {"radicalmart-ajax": "products"}).find("div", class_="products-list")
    if not products:
        return
    cards = products.find_all(
        "div",
        class_="uk-card uk-card-default uk-card-small uk-card-body uk-card-hover tm-product-card"
    )
    for card in cards:
        details_link = card.find_all("a", class_="uk-link-reset")[-1].get("href")
        direct_link = f"{domain_url}{details_link}"
        await get_stone_info(direct_link, domain_url)


async def parse_stones():
    domain: str = "https://market.region-zoloto.ru"
    url_to_stones_page: str = f"{domain}/katalog/brillianty/laboratornye-brillianty"
    stones_page = await get_page(url_to_stones_page)
    await get_stones_data(stones_page, domain)
