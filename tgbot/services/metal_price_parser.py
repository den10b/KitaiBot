from bs4 import BeautifulSoup
from database.models import CityInfo, MetalToSalePrice, MetalToSale
import aiohttp
import asyncio


async def update_metal_price_db(response_text: str, city: CityInfo):
    soup = BeautifulSoup(response_text, "html.parser")
    metal_tables_list = soup.find("ul", class_="uk-switcher uk-margin-top uk-switcher-metal-all").findChildren(
        recursive=False)
    for table, metal in zip(metal_tables_list, ['Золото', 'Серебро', 'Платина', 'Палладий']):
        comments = []
        headers_list = table.find("table", class_="uk-table uk-table-striped table-prices").find("tr",
                                                                                                 class_="tr-subhead").findChildren(
            recursive=False)
        for header in headers_list[1:]:
            comments.append(header.text)
        comment_iter = iter(comments)
        metal_to_sale, created = MetalToSale.objects.get_or_create(metal=metal,
                                                                   city_id=city)
        metal_to_sale.cash_comment = next(comment_iter, None)
        metal_to_sale.card_comment = next(comment_iter, None)
        metal_to_sale.transfer_comment = next(comment_iter, None)
        metal_to_sale.save()
        rows_list = table.find("tbody").findChildren(recursive=False)
        for row in rows_list:
            fields_list = row.findChildren(recursive=False)
            probe = fields_list[0].text.strip()  # Первое поле в таблице - проба
            price_fields = []
            for field in fields_list[1:]:  # Все остальные поля - цена
                try:
                    price_fields.append(float(field.find("span", class_="pr").text))
                except:
                    price_fields.append(float(0.0))

            price_fields_iter = iter(price_fields)
            metal_to_sale_price, created_2 = MetalToSalePrice.objects.get_or_create(metal_id=metal_to_sale,
                                                                                    proba=probe)
            metal_to_sale_price.cash_price = next(price_fields_iter, None)
            metal_to_sale_price.card_price = next(price_fields_iter, None)
            metal_to_sale_price.transfer_price = next(price_fields_iter, None)
            metal_to_sale_price.save()

    return True


async def get_prices_tables():
    for city in CityInfo.objects.all():
        domain = city.link
        url = f"{domain}/skupka"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.text()
        correct = await update_metal_price_db(response, city)
