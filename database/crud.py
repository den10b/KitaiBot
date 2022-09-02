import uvicorn as uvicorn

from .models import BrandModel, ModelModel, ProductModel, DealModel, GroupModel, UserModel, MailingModel
from .schemas import *
from .database_conf import get_db, SessionLocal
from fastapi_crudrouter import SQLAlchemyCRUDRouter

# with SessionLocal() as session:
#     query = session.query(ModelModel, BrandModel)
#     query = query.join(BrandModel, BrandModel.id == ModelModel.brand_id)
#     records = query.all()
#
#     for model, brand in records:
#         print(model)
#         print(brand)
#         print("{0} под брендом {1}".format(model.model, brand.brand))

Brand_router = SQLAlchemyCRUDRouter(
    schema=Brand,
    create_schema=BrandIn,
    db_model=BrandModel,
    db=get_db,
    prefix='brand'
)

Model_router = SQLAlchemyCRUDRouter(
    schema=Model,
    create_schema=ModelIn,
    db_model=ModelModel,
    db=get_db,
    prefix='model'
)

Product_router = SQLAlchemyCRUDRouter(
    schema=Product,
    create_schema=ProductIn,
    db_model=ProductModel,
    db=get_db,
    prefix='product'
)

Deal_router = SQLAlchemyCRUDRouter(
    schema=Deal,
    create_schema=DealIn,
    db_model=DealModel,
    db=get_db,
    prefix='deal'
)

Group_router = SQLAlchemyCRUDRouter(
    schema=Group,
    create_schema=GroupIn,
    db_model=GroupModel,
    db=get_db,
    prefix='group'
)

User_router = SQLAlchemyCRUDRouter(
    schema=User,
    create_schema=UserIn,
    db_model=UserModel,
    db=get_db,
    prefix='user'
)

Mailing_router = SQLAlchemyCRUDRouter(
    schema=Mailing,
    create_schema=MailingIn,
    db_model=MailingModel,
    db=get_db,
    prefix='mailing'
)
