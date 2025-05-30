from fastapi import FastAPI
from routes.book_route import book_router
from routes.user_route import auth_router
from routes.review_route import review_router


# @asynccontextmanager
# async def lifespan(app:FastAPI):
#     print("Starting up...")
#     await init_db()
#     yield
#     print("Shutting down...")

app = FastAPI()

app.include_router(book_router, prefix="/books", tags=["books"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(review_router, prefix="/reviews", tags=["reviews"])

@app.get("/")
async def root():
    return {"message": "Hello World"}

