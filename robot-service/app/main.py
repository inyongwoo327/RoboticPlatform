from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import logging
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.models import Robot, RobotUpdate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

robots_db = []

robot_added_counter = Counter("robots_added_total", "Total robots added")
request_duration = Histogram("request_duration_seconds", "Request duration in seconds", ["endpoint"])

@app.get("/robots", response_model=List[Robot])
async def get_robots():
    with request_duration.labels(endpoint="/robots").time():
        logger.info("Fetching all robots")
        return robots_db

@app.post("/robots", response_model=Robot)
async def add_robot(robot: Robot):
    with request_duration.labels(endpoint="/robots").time():
        if any(r.id == robot.id for r in robots_db):
            logger.error(f"Robot with ID {robot.id} already exists")
            raise HTTPException(status_code=400, detail="Robot ID already exists")
        robots_db.append(robot)
        robot_added_counter.inc()
        logger.info(f"Added robot: {robot.id}")
        return robot

@app.patch("/robot/{robot_id}", response_model=Robot)
async def update_robot(robot_id: str, update: RobotUpdate):
    with request_duration.labels(endpoint="/robot").time():
        for robot in robots_db:
            if robot.id == robot_id:
                if update.name:
                    robot.name = update.name
                if update.status:
                    robot.status = update.status
                logger.info(f"Updated robot: {robot_id}")
                return robot
        logger.error(f"Robot with ID {robot_id} not found")
        raise HTTPException(status_code=404, detail="Robot not found")

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)