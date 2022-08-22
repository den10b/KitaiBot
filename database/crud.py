from models import *
from schemas import *
from database.database import get_db
from fastapi import FastAPI
from fastapi_crudrouter import SQLAlchemyCRUDRouter

app = FastAPI()
router = SQLAlchemyCRUDRouter(
    schema=Brand,
    create_schema=BrandIn,
    db_model=BrandModel,
    db=get_db,
    prefix='brand'
)

app.include_router(router)