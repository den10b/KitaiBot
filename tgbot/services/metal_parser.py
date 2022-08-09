from bs4 import BeautifulSoup
from database.models import MetalToBuy
import aiohttp
import asyncio


async def get_metals_data(response_text: str, base_url: str):
    soup = BeautifulSoup(response_text, "html.parser")
    all_items = soup.find("div", id="page#31").find("div",
                                                    class_="uk-child-width-1-1 uk-child-width-1-3@m uk-grid-match"
                                                    ).findChildren(recursive=False)
    for item in all_items:
        prices = item.find("div",
                           class_="uk-height-1-1 uk-flex uk-flex-wrap uk-text-center uk-text-right@m uk-flex-middle "
                                  "uk-text-large uk-text-bold")
        price = prices.find("div", "uk-width-1-1 uk-text-nowrap").text.split("₽")[0].replace(' ', '')
        if price != "недоступно":
            price = int(price)
        else:
            break
        price_nds = prices.find("div", "uk-width-1-1 uk-text-nowrap uk-text-default")
        if price_nds is not None:
            price_nds = int(price_nds.text.split("₽")[0].replace(' ', ''))
        else:
            price_nds = price
        full_item = item.find("a", class_="uk-link-reset")
        description = await get_metal_shop_items(full_item.get("href"))
        link_to_img = item.find("img").get("data-src")
        if link_to_img.startswith("/"):
            link_to_img = base_url + link_to_img
        full_item = full_item.text.split(" ")
        metal_name = full_item[0].strip()
        item_type = full_item[3]
        match item_type:
            case "гранулах":
                item_type = MetalToBuy.Sort.GRANULE
            case "мерных":
                item_type = MetalToBuy.Sort.BULLION_BARS
            case "стандартных":
                break
                item_type = MetalToBuy.Sort.BULLION_STANDARD
            case "порошке":
                item_type = MetalToBuy.Sort.POWDER
            case "слитках":
                item_type = MetalToBuy.Sort.BULLION
            case "пластинах":
                item_type = MetalToBuy.Sort.PLATE
        try:
            metal_to_buy,created = MetalToBuy.objects.get_or_create(name=metal_name, sort=item_type)
            metal_to_buy.image = link_to_img
            metal_to_buy.description = description
            metal_to_buy.price_with_nds = price_nds
            metal_to_buy.price_without_nds = price
            metal_to_buy.save()
        except Exception as e:
            print(e)
            MetalToBuy(name=metal_name,
                       sort=item_type,
                       image=link_to_img,
                       description=description,
                       price_with_nds=price_nds,
                       price_without_nds=price).save()

    return True


def get_metal_descr(response_text: str):
    metal_descr = ''
    soup = BeautifulSoup(response_text, "html.parser")
    all_fields = soup.find("ul", id="page#17")
    if all_fields is None:
        all_fields = soup.find("ul", id="page#18")
        if all_fields is None:
            return ""
    all_fields = all_fields.findChildren(recursive=False)
    for field in all_fields:
        field_text = field.find("div").text
        if not str(field_text).__contains__("Название производителя"):
            metal_descr += field_text + '\n'
    return metal_descr


async def get_metal_shop_items(shop_item: str = '/shop'):
    domain = "https://www.region-zoloto.ru"
    url = f"{domain}{shop_item}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            response = await resp.text()
    if shop_item != '/shop':
        return get_metal_descr(response)
    else:
        return await get_metals_data(response, domain)
