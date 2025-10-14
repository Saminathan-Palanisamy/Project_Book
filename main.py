from fastapi import FastAPI
from routers import books, authors, users, purchases
from core.database import Base, engine


#from routers import views

# Create tables automatically (optional)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sajith Books API - Role Based Access Control")


# Include routers

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(authors.router, prefix="/authors", tags=["Authors"])


# Purchase router
app.include_router(purchases.router, prefix="/purchases", tags=["Purchases"])

# Root endpoint
@app.get("/")
def root():
    return {"message": "Book Management API - Welcome to the book world of Sajith!"}