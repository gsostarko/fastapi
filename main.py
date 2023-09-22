from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv 
from pushbullet import Pushbullet
import os
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


load_dotenv('.env')             #os.getenv('SECRET_KEY')

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static", html=True), name="static")


pb = Pushbullet(os.getenv("PUSHBULLET_API_KEY"))



def push(data):
    value = data["timestamp"]
    pb.push_note("ESP32",f"The last timestamp is: {value}")
    print(data)

# Define your database connection URL


# Create a SQLAlchemy engine and session
engine = create_engine(os.getenv("API_DATABASE_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Define your data model
class SensorData(Base):
    __tablename__ = "data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String)
    time = Column(String)
    temperature = Column(Float)
    humidity = Column(Float)
    soc = Column(Integer)

# Initialize the FastAPI app
app = FastAPI()

# Pydantic model for data validation
class ValidationData(BaseModel):
    timestamp: str
    time: str
    temperature: float
    humidity: float
    soc: int

@app.post("/data",
         summary="Measurement input",
         description="Saves timestamp, temperature, humidity and battery SoC in the database")
async def upload_data(data: ValidationData):
    try:
        # Create a new record in the database
        db = SessionLocal()
        db_data = SensorData(data)
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        db.close()
        #date_data = data_input.split("---",1)
        #print(date_data[1])
        #time = date_data[1].split(".",3)
        #print(time[0], time[1])
        
        return {"message": "Data saved successfully",
              "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        #return {"message": data_input}

@app.get("/get-last/",
        summary = "Get last row of database",
        description = "Returns the last measurement from the database")
async def get_last_data():
    try:
        # Create a new database session
        db = SessionLocal()

        # Query the database to get the last row
        last_data = db.query(SensorData).order_by(SensorData.id.desc()).first()
        push(last_data)
        db.close()

        if last_data is None:
            raise HTTPException(statusdata_input_code=404, detail="No data found")
        # Convert the last data to a dictionary and return it
        return last_data.__dict__
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-all/")
async def get_all(request: Request):
    try:
        db = SessionLocal()

        all_data = db.query(SensorData).all()
        db.close()

        if all_data is None:
            raise HTTPException(statusdata_input_code = 404, detail="No data found")
        return templates.TemplateResponse("get-all.html", {"request" : request, "data": all_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
