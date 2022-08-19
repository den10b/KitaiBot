from pydantic import BaseModel
from uuid import uuid4, UUID


class BrandIn(BaseModel):
    brand: str


class Brand(BrandIn):
    id: UUID

    class Config:
        orm_mode = True


class ModelIn(BaseModel):
    model: str
    brand_id: list[Brand] = []


class Model(ModelIn):
    id: UUID

    class Config:
        orm_mode = True
