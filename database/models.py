from django.db import models


class ModelInfo(models.Model):
    """
    Модель от которой наследуемся. Каждая модель будет иметь поля:
    1. Дата создания.
    2. Дата изменения.
    """
    date_create = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    date_update = models.DateTimeField(verbose_name='Дата изменения', auto_now=True)

    class Meta:
        abstract = True


class TgUser(ModelInfo):
    """
    Модель пользователя телеграм.
    """
    user_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=128, null=True)
    phone_number = models.CharField(max_length=30, null=True)
    name = models.CharField(max_length=128, null=True, default=None)
    email = models.EmailField(null=True, default=None)
    news = models.BooleanField(default=False)

    class Meta:
        verbose_name = "ПользовательТг"

    def is_admin(self):
        if TgAdmin.objects.filter(user_id=self.user_id).first():
            return True
        return False


class TgAdmin(ModelInfo):
    """
    Модель администратора.
    """
    user_id = models.OneToOneField(TgUser, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "АдминТг"


class Review(ModelInfo):
    """
    Отзывы/Идеи.
    """
    user_id = models.ForeignKey(TgUser, on_delete=models.CASCADE)
    text = models.CharField(max_length=250)

    class Meta:
        verbose_name = "Отзыв/Идея"


class ReviewData(ModelInfo):
    """
    Файлы для модели отзывов/идей.
    """
    review_id = models.ForeignKey(Review, on_delete=models.CASCADE)
    file_id = models.CharField(max_length=250)

    class Meta:
        verbose_name = "Файл для Отзыв/Идея"


class BackCall(ModelInfo):
    """
    Заказать обратный звонок.
    """
    user_id = models.ForeignKey(TgUser, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=30)
    datetime_call = models.DateTimeField()

    class Meta:
        verbose_name = "Обратный звонок"


class CityInfo(ModelInfo):
    """
    Контакты филиалов.
    """
    city = models.CharField(max_length=30)
    link = models.CharField(max_length=100, default='https://www.region-zoloto.ru/')

    class Meta:
        verbose_name = "Филиал"


class CityAddress(ModelInfo):
    city_id = models.ForeignKey(CityInfo, on_delete=models.CASCADE)
    address = models.CharField(max_length=140)


class CityPhoneNumbers(ModelInfo):
    """
    Номера телефонов для филиала.
    """
    city_info_id = models.ForeignKey(CityInfo, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=30)
    comment = models.CharField(max_length=80)

    class Meta:
        verbose_name = "Контакты филиала"


class MetalToBuy(ModelInfo):
    """
    Информация о металле для покупки.
    """

    class Sort(models.TextChoices):
        GRANULE = 'Гранула'
        BULLION = 'Слиток'
        BULLION_BARS = 'Мерный слиток'
        BULLION_STANDARD = 'Стандартный слиток'
        POWDER = 'Порошок'
        PLATE = 'Пластина'

    name = models.CharField(max_length=30)
    image = models.CharField(max_length=300)
    description = models.CharField(max_length=800)
    sort = models.CharField(max_length=30, choices=Sort.choices)
    price_with_nds = models.IntegerField()
    price_without_nds = models.IntegerField()


class GemToBuy(ModelInfo):
    """
    Информация о камнях для покупки.
    """

    class Form(models.TextChoices):
        R57 = 'Круглый'
        CUSHION = 'Кушон'
        MARQUISE = 'Маркиз'
        OVAL = 'Овал'
        PEAR = 'Груша'

    class DefGia(models.TextChoices):
        VS1 = 'VS1'
        VVS1 = 'VVS1'
        SI1 = 'SI1'
        SI2 = 'SI2'

    form = models.CharField(max_length=30, choices=Form.choices)
    image = models.CharField(max_length=300)
    size = models.CharField(max_length=30)
    def_gia = models.CharField(max_length=10, choices=DefGia.choices)
    price = models.IntegerField()


class FAQ(ModelInfo):
    """
    Вопросы и ответы.
    """
    question = models.CharField(max_length=100)
    answer = models.TextField(max_length=500)


class Sales(ModelInfo):
    """
    Главная модель продаж.
    """

    class Status(models.TextChoices):
        NEW = 'Новый'
        CREATED = 'Созданный'
        CONFIRMED = 'Подтвержден менеджером'

    user_id = models.ForeignKey(TgUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=Status.choices)
    city = models.ForeignKey(CityInfo, on_delete=models.CASCADE, null=True, default=None)
    phone_number = models.CharField(max_length=30, null=True, default=None)


class Basket(ModelInfo):
    """
    Корзина. Добавляем либо метал, либо камни и выбираем кол-во.
    """
    sales_id = models.ForeignKey(Sales, on_delete=models.CASCADE)
    metal_id = models.ForeignKey(MetalToBuy, on_delete=models.CASCADE, null=True, default=None)
    gem_id = models.ForeignKey(GemToBuy, on_delete=models.CASCADE, null=True, default=None)
    count = models.IntegerField(default=1)


class MetalToSale(ModelInfo):
    class MetalName(models.TextChoices):
        gold = 'Золото'
        silver = 'Серебро'
        platinum = 'Платина'
        palladium = 'Палладий'

    metal = models.CharField(max_length=30, choices=MetalName.choices)
    city_id = models.ForeignKey(CityInfo, on_delete=models.CASCADE)
    cash_comment = models.CharField(max_length=50, null=True)
    card_comment = models.CharField(max_length=50, null=True)
    transfer_comment = models.CharField(max_length=50, null=True)


class MetalToSalePrice(ModelInfo):
    metal_id = models.ForeignKey(MetalToSale, on_delete=models.CASCADE)
    proba = models.CharField(max_length=30)
    cash_price = models.FloatField(null=True)
    card_price = models.FloatField(null=True)
    transfer_price = models.FloatField(null=True)


class News(ModelInfo):
    word = models.CharField(max_length=30)
    title = models.CharField(max_length=150)
    direct_link = models.CharField(max_length=150)
    preview_image_link = models.CharField(max_length=150)
    description = models.CharField(max_length=1000)
    is_send = models.BooleanField(default=False)


class UserNews(ModelInfo):
    user_id = models.ForeignKey(TgUser, on_delete=models.CASCADE)
    word = models.CharField(max_length=30)
