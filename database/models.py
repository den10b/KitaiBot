import enum
import uuid
from sqlalchemy import TIMESTAMP

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Enum, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from sqlalchemy.orm import relationship

from database.database_conf import Base


class BrandModel(Base):
    __tablename__ = "brands"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    brand = Column(String)

    models = relationship("ModelModel", backref="brand")


class ModelModel(Base):
    __tablename__ = "models"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    model = Column(String)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id"))

    products = relationship("ProductModel", backref="model")


class ProductModel(Base):
    __tablename__ = 'products'
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    size = Column(Float)
    price = Column(Float)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"))

    deals = relationship("DealModel", backref="product")


class MyEnum(enum.Enum):
    one = 1
    two = 2
    three = 3


class DealModel(Base):
    __tablename__ = 'deals'
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    status = Column(Enum(MyEnum))
    time = Column(TIMESTAMP)
    description = Column(Text)
    qr_code = Column(BYTEA)
    image = Column(BYTEA)
    transaction = Column(Enum(MyEnum))
    user_id = Column(BigInteger, ForeignKey("users.tg_id"))


class GroupModel(Base):
    __tablename__ = 'groups'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text)


users = relationship("UserModel", backref="group")
messages = relationship("MailingModel", backref="group")


class UserModel(Base):
    __tablename__ = 'users'
    tg_id = Column(BigInteger, primary_key=True)
    tg_tag = Column(Text)
    password = Column(Text)
    group_id = Column(UUID(as_uuid=True), ForeignKey('groups.id'))
    is_logined = Column(Boolean, default=False)


deals = relationship("DealModel", backref="user")


class MailingModel(Base):
    __tablename__ = 'messages'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text)
    text = Column(Text)
    status = Column(Enum(MyEnum))
    time_to_send = Column(TIMESTAMP)
    group_id = Column(UUID, ForeignKey('groups.id'))
