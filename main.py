from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import pywhatkit

#TEST
import http.client, urllib

def push():
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.parse.urlencode({
    "token": "awo869wegvuxbiriutyexs3y1e2ys5",
    "user": "u7923r1cewg4si6vuoqxg7umgj3638",
    "message": "hello world",
  }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()



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

@app.get("/upload/{data_input}",
         summary="Measurement input",
         description="Saves timestamp, temperature, humidity and battery SoC in the database")
async def upload_data(data_input: str):
    try:
        # Create a new record in the database
        db = SessionLocal()
        db_data = SensorData(timestamp=data_input)
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        db.close()
        date_data = data_input.split("---",1)
        print(date_data[1])
        time = date_data[1].split(".",3)
        print(time[0], time[1])
        pywhatkit.sendwhatmsg('+385981372306', data_input, int(time[0]), int(time[1])+1)
        return {"message": "Data saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        return {"message": data_input}

@app.get("/get-last/",
        summary = "Get last row of database",
        description = "Returns the last measurement from the database")
async def get_last_data():
    try:
        # Create a new database session
        db = SessionLocal()

        # Query the database to get the last row
        last_data = db.query(SensorData).order_by(SensorData.id.desc()).first()

        db.close()

        if last_data is None:
            raise HTTPException(status_code=404, detail="No data found")

        # Convert the last data to a dictionary and return it
        return last_data.__dict__

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    push()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
