import uvicorn as uvicorn

from models import BrandModel, ModelModel, ProductModel, DealModel, GroupModel, UserModel, MailingModel
from schemas import *
from database_conf import get_db
from fastapi import FastAPI
from fastapi_crudrouter import SQLAlchemyCRUDRouter

app = FastAPI()
Brandrouter = SQLAlchemyCRUDRouter(
    schema=Brand,
    create_schema=BrandIn,
    db_model=BrandModel,
    db=get_db,
    prefix='brand'
)

app.include_router(Brandrouter)

Modelrouter = SQLAlchemyCRUDRouter(
    schema=Model,
    create_schema=ModelIn,
    db_model=ModelModel,
    db=get_db,
    prefix='model'
)

app.include_router(Modelrouter)

Productrouter = SQLAlchemyCRUDRouter(
    schema=Product,
    create_schema=ProductIn,
    db_model=ProductModel,
    db=get_db,
    prefix='product'
)

app.include_router(Productrouter)

Dealrouter = SQLAlchemyCRUDRouter(
    schema=Deal,
    create_schema=DealIn,
    db_model=DealModel,
    db=get_db,
    prefix='deal'
)

app.include_router(Dealrouter)

Grouprouter = SQLAlchemyCRUDRouter(
    schema=Group,
    create_schema=GroupIn,
    db_model=GroupModel,
    db=get_db,
    prefix='group'
)

app.include_router(Grouprouter)

Userrouter = SQLAlchemyCRUDRouter(
    schema=User,
    create_schema=UserIn,
    db_model=UserModel,
    db=get_db,
    prefix='user'
)

app.include_router(Userrouter)

Mailingrouter = SQLAlchemyCRUDRouter(
    schema=Mailing,
    create_schema=MailingIn,
    db_model=MailingModel,
    db=get_db,
    prefix='mailing'
)

app.include_router(Userrouter)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)