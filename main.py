#from fastapi import FastAPI

#app = FastAPI()

#@app.get("/")
#async def root():
#    return {"greeting": "Hello, World!", "message": "Welcome to FastAPI!"}

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Replace these with your database credentials
DATABASE_URL = "postgresql://username:password@localhost/dbname"

# Create a SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a SQLAlchemy Base object
Base = declarative_base()

# Define the SQLAlchemy model for the database table
class StringData(Base):
    __tablename__ = "string_data"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(String, index=True)

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Pydantic model for the incoming data
class DataInput(BaseModel):
    data: str

# Create a route to handle the POST request
@app.post("/store-data/")
async def store_data(data_input: DataInput):
    # Create a new record in the database
    db = SessionLocal()
    db_data = StringData(data=data_input.data)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    db.close()
    return {"message": "Data stored successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
