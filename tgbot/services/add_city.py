from loguru import logger

from database.models import CityAddress, CityInfo, CityPhoneNumbers


async def add_city_data():
    data = [
        {'city': 'Москва',
         'link': 'https://www.region-zoloto.ru/',
         'address': ['г. Москва, Большой Черкасский пер. д. 4 стр. 1, первый этаж',
                     'г. Москва, Цветной бульвар д. 26, стр. 1, офис 26, 2 этаж',
                     'г. Москва, улица Василисы Кожиной, 13'],
         'phone': [
             ['8 800 250-56-62', 'Бесплатный звонок'],
             ['+7 985 281 95 77 ', 'Звонок из Москвы'],
         ]},

        {'city': 'Санкт-Петербруг',
         'link': 'https://spb.region-zoloto.ru/',
         'address': ['г. Санкт-Петербург, ул. Заставская д.46 к.1 офис 20н'],
         'phone': [
             ['8 800 250-56-62', 'Бесплатный звонок'],
             ['8 (812) 602-17-64 ', 'Звонок из Санкт-Петербурга'],
         ]},

        # {'city': 'Брянск',
        #  'link': 'https://bryansk.region-zoloto.ru/',
        #  'address': ['г. Брянск'],
        #  'phone': [
        #      ['8 800 250-56-62', 'Бесплатный звонок']
        #  ]},

        {'city': 'Новосибирск',
         'link': 'https://nsk.region-zoloto.ru/',
         'address': ['г. Новосибирск, улица Фрунзе, 242 офис 515'],
         'phone': [
             ['8 800 250-56-62', 'Бесплатный звонок'],
             ['8 (383) 383-05-10 ', 'Звонок из Новосибирска'],
         ]},

        {'city': 'Кострома',
         'link': 'https://kostroma.region-zoloto.ru/',
         'address': ['Костромская область, г. Кострома, ул. Советская, д. 19'],
         'phone': [
             ['8 800 250-56-62', 'Бесплатный звонок'],
             ['8 (4942) 30-11-57 ', 'Звонок из Костромы'],
         ]},

        {'city': 'Калининград',
         'link': 'https://kaliningrad.region-zoloto.ru/',
         'address': ['г. Калининград, ул. Черняховского, 15'],
         'phone': [
             ['8 800 250-56-62', 'Бесплатный звонок'],
             ['8 (4012) 96-53-45  ', 'Звонок из Калининграда'],
         ]},

        {'city': 'Ростов-На-Дону',
         'link': 'https://rostov-na-donu.region-zoloto.ru/',
         'address': ['г. Ростов-на-Дону, пр-кт Чехова, дом 37/29, комната 17'],
         'phone': [
             ['8 800 250-56-62', 'Бесплатный звонок'],
             ['8 (863) 296-44-99', 'Звонок из Ростова-На-Дону'],
         ]},
    ]
    counter = 0
    logger.info('Добавляю города! ')
    for value in data:
        city, created = CityInfo.objects.get_or_create(city=value['city'], link=value['link'])
        if created:
            counter += 1
            for address in value['address']:
                CityAddress.objects.get_or_create(city_id=city, address=address)
            for phone in value['phone']:
                CityPhoneNumbers.objects.get_or_create(city_info_id=city,
                                                       phone_number=phone[0],
                                                       comment=phone[1])
    logger.info(f'Добавил {counter} городов!')
