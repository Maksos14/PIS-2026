from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import datetime
import uuid

app = FastAPI(title="Group Service")

# Хранилище в памяти
groups = {}

class Group:
    def __init__(self, id: str, name: str, leader_id: str):
        self.id = id
        self.name = name
        self.leader_id = leader_id
        self.member_ids = [leader_id]
        self.status = "forming"
        self.created_at = datetime.now()

class CreateGroupRequest(BaseModel):
    name: str
    leader_id: str

class AddMemberRequest(BaseModel):
    member_id: str

@app.post("/api/groups")
def create_group(req: CreateGroupRequest):
    group_id = f"GRP-{uuid.uuid4().hex[:4].upper()}"
    group = Group(group_id, req.name, req.leader_id)
    groups[group_id] = group
    return {"group_id": group_id}

@app.get("/api/groups/{group_id}")
def get_group(group_id: str):
    group = groups.get(group_id)
    if not group:
        return {"error": "Not found"}, 404
    return {
        "id": group.id,
        "name": group.name,
        "leader_id": group.leader_id,
        "member_ids": group.member_ids,
        "status": group.status
    }

@app.post("/api/groups/{group_id}/members")
def add_member(group_id: str, req: AddMemberRequest):
    group = groups.get(group_id)
    if not group:
        return {"error": "Not found"}, 404
    if req.member_id not in group.member_ids:
        group.member_ids.append(req.member_id)
    if len(group.member_ids) >= 3 and group.status == "forming":
        group.status = "ready"
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
