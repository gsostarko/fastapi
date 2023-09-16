from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define your database connection URL
DATABASE_URL = "postgresql://postgres:eYl7DP0W10K3DMUH25md@containers-us-west-98.railway.app:6807/railway"

# Create a SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Define your data model
class SensorData(Base):
    __tablename__ = "data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String)

# Initialize the FastAPI app
app = FastAPI()

# Pydantic model for data validation
class DataInput(str):
    data: str

@app.get("/upload/{data_input}")
async def upload_data(data_input: str):
    try:
        # Create a new record in the database
        db = SessionLocal()
        db_data = SensorData(timestamp=data_input)
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        db.close()
        return {"message": "Data saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        return {"message": data}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
