import enum

from sqlalchemy import TIMESTAMP

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Enum, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from sqlalchemy.orm import relationship

from .database import Base


class Brand(Base):
    __tablename__ = "brands"

    id = Column(UUID, primary_key=True, index=True)
    brand = Column(String)

    models = relationship("Models", back_populates="brand")


class Model(Base):
    __tablename__ = "models"

    id = Column(UUID, primary_key=True, index=True)
    model = Column(String)
    brand_id = Column(UUID, ForeignKey("brands.id"))

    products = relationship("Product", back_populates="model")


class Product(Base):
    __tablename__ = 'products'
    id = Column(UUID, primary_key=True, index=True)
    size = Column(Float)
    price = Column(Float)
    model_id = Column(UUID, ForeignKey("models.id"))

    deals = relationship("Deal", back_populates="product")


class MyEnum(enum.Enum):
    one = 1
    two = 2
    three = 3


class Deal(Base):
    __tablename__ = 'deals'
    id = Column(UUID, primary_key=True, index=True)
    product_id = Column(UUID, ForeignKey("products.id"))
    status = Column(Enum(MyEnum))
    time = Column(TIMESTAMP)
    description = Column(Text)
    qr_code = Column(BYTEA)
    image = Column(BYTEA)
    transaction = Column(Enum(MyEnum))
    user_id = Column(BigInteger, ForeignKey("users.id"))


class Group(Base):
    __tablename__ = 'groups'
    id = Column(UUID, primary_key=True)
    name = Column(Text)


users = relationship("User", back_populates="group")
messages = relationship("Mailing", back_populates="group")


class User(Base):
    __tablename__ = 'users'
    tg_id = Column(BigInteger, primary_key=True)
    tg_tag = Column(Text)
    group_id = Column(UUID, ForeignKey('groups.id'))


deals = relationship("Deal", back_populates="user")


class Mailing(Base):
    __tablename__ = 'Messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    text = Column(Text)
    status = Column(Enum(MyEnum))
    time_to_send = Column(TIMESTAMP)
    group_id = Column(UUID, ForeignKey('groups.id'))
