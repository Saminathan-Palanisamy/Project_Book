from fastapi import FastAPI
from routers import books, authors, users
from core.database import Base, engine

# Create tables automatically (optional)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sajith Books API")

# Include routers
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(authors.router, prefix="/authors", tags=["Authors"])
app.include_router(users.router, prefix="/users", tags=["Users"])
