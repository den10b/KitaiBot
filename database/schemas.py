import datetime

from pydantic import BaseModel
from uuid import uuid4, UUID
from enum import Enum, IntEnum


class BrandIn(BaseModel):
    brand: str


class Brand(BrandIn):
    id: UUID

    class Config:
        orm_mode = True


class ModelIn(BaseModel):
    model: str
    brand_id: UUID


class Model(ModelIn):
    id: UUID

    class Config:
        orm_mode = True


class ProductIn(BaseModel):
    size: float
    price: float
    model_id: UUID


class Product(ProductIn):
    id: UUID

    class Config:
        orm_mode = True


class GroupIn(BaseModel):
    name: str


class Group(GroupIn):
    id: UUID

    class Config:
        orm_mode = True


class UserIn(BaseModel):
    tg_tag: str
    group_id: UUID


class User(UserIn):
    tg_id: int

    class Config:
        orm_mode = True


class MyEnum(IntEnum):
    one = 1
    two = 2
    three = 3


class DealIn(BaseModel):
    product_id: UUID
    status: str
    description: str
    qr_code: bytes
    image: bytes
    transaction: str
    user_id: int


class Deal(DealIn):
    id: UUID
    time: datetime.datetime

    class Config:
        orm_mode = True


class MailingIn(BaseModel):
    name: str
    text: str
    status: str
    group_id: UUID


class Mailing(MailingIn):
    id: UUID
    time: datetime.datetime

    class Config:
        orm_mode = True
