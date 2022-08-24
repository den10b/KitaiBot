from fastapi import FastAPI
from database.crud import Brand_router, Model_router, Product_router, Deal_router, Group_router, User_router, Mailing_router

app = FastAPI()

# crud
app.include_router(Brand_router)
app.include_router(Model_router)
app.include_router(Product_router)
app.include_router(Deal_router)
app.include_router(Group_router)
app.include_router(User_router)
app.include_router(Mailing_router)

