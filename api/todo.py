import os
import time
from uuid import uuid4
from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel
from typing import Optional
import boto3

app = FastAPI()
handler = Mangum(app)


class PutTaskRequest(BaseModel):
    content: str
    user_id: Optional[str] = None
    task_id: Optional[str] = None
    is_done: bool = False


@app.get("/")
async def root():
    return {"message": "Hello from Todo API!"}


@app.put("/create-task")
async def create_task(put_task_request: PutTaskRequest):
    created_time = int(time.time())
    item = {
        "user_id": put_task_request.user_id,
        "content": put_task_request.content,
        "is_done": False,
        "created_time": created_time,
        "task_id": f"task_{uuid4().hex}",
        "ttl": int(created_time + 86400),  # Expire after 24 hours.
    }
    
    # Put it into the table.
    table = _get_table()
    table.put_item(Item=item)
    return {"task": item}
    

def _get_table():
    table_name = os.environ.get("TABLE_NAME")
    return boto3.resource("dynamodb").Table(table_name)