import grpc
from concurrent import futures
import time
import uuid
from datetime import datetime
from typing import Dict
from queue import Queue

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from generated.request_service_pb2 import (
    CreateOfferRequest, CreateOfferResponse,
    GetOfferRequest, Offer,
    ChangeStageRequest, ChangeStageResponse,
    AddNoteRequest, AddNoteResponse,
    RejectOfferRequest, RejectOfferResponse,
    ListActiveOffersRequest, ListActiveOffersResponse,
    OfferSummary, OfferUpdate, StreamOfferUpdatesRequest
)
from generated.request_service_pb2_grpc import RequestServiceServicer, add_RequestServiceServicer_to_server

from generated.group_service_pb2 import (
    CreateGroupRequest, CreateGroupResponse,
    GetGroupRequest, Group,
    AddMemberRequest, AddMemberResponse,
    ListUserGroupsRequest, ListUserGroupsResponse,
    GroupSummary
)
from generated.group_service_pb2_grpc import GroupServiceServicer, add_GroupServiceServicer_to_server

# Хранилища
offers: Dict[str, dict] = {}
groups: Dict[str, dict] = {}
active_streams: Dict[str, list] = {}


class RequestServiceServicerImpl(RequestServiceServicer):
    
    def CreateOffer(self, request, context):
        offer_id = f"OFFER-2024-{uuid.uuid4().hex[:4].upper()}"
        offers[offer_id] = {
            "id": offer_id,
            "company": request.company,
            "position": request.position,
            "user_id": request.user_id,
            "status": "active",
            "current_stage": "resume_sent",
            "progress_percentage": 0.0,
            "notes": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return CreateOfferResponse(offer_id=offer_id, status="created")
    
    def GetOffer(self, request, context):
        offer = offers.get(request.offer_id)
        if not offer:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return Offer()
        return Offer(
            id=offer["id"],
            company=offer["company"],
            position=offer["position"],
            user_id=offer["user_id"],
            status=offer["status"],
            current_stage=offer["current_stage"],
            progress_percentage=offer["progress_percentage"],
            notes=offer["notes"],
            created_at=offer["created_at"],
            updated_at=offer["updated_at"]
        )
    
    def ChangeStage(self, request, context):
        offer = offers.get(request.offer_id)
        if not offer:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return ChangeStageResponse()
        
        stages = ["resume_sent", "hr_screening", "tech_interview", "test_task", "final_interview", "offer"]
        old_stage = offer["current_stage"]
        old_idx = stages.index(old_stage)
        new_idx = stages.index(request.new_stage)
        
        if new_idx <= old_idx:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return ChangeStageResponse()
        if new_idx > old_idx + 1:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return ChangeStageResponse()
        
        offer["current_stage"] = request.new_stage
        offer["progress_percentage"] = (new_idx / (len(stages) - 1)) * 100
        offer["updated_at"] = datetime.now().isoformat()
        
        if request.note:
            offer["notes"].append(request.note)
        
        if request.new_stage == "offer":
            offer["status"] = "offer_received"
        
        return ChangeStageResponse(offer_id=request.offer_id, old_stage=old_stage, new_stage=request.new_stage)
    
    def AddNote(self, request, context):
        offer = offers.get(request.offer_id)
        if not offer:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return AddNoteResponse()
        offer["notes"].append(request.content)
        offer["updated_at"] = datetime.now().isoformat()
        return AddNoteResponse(offer_id=request.offer_id, notes_count=len(offer["notes"]))
    
    def RejectOffer(self, request, context):
        offer = offers.get(request.offer_id)
        if not offer:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return RejectOfferResponse()
        if offer["status"] == "offer_received":
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return RejectOfferResponse()
        
        old_status = offer["status"]
        offer["status"] = "rejected"
        offer["updated_at"] = datetime.now().isoformat()
        return RejectOfferResponse(offer_id=request.offer_id, old_status=old_status, new_status="rejected")
    
    def ListActiveOffers(self, request, context):
        user_offers = [o for o in offers.values() if o["user_id"] == request.user_id]
        active = [o for o in user_offers if o["status"] in ["active", "offer_received"]]
        items = [OfferSummary(
            id=o["id"],
            company=o["company"],
            position=o["position"],
            current_stage=o["current_stage"],
            progress_percentage=o["progress_percentage"]
        ) for o in active[:request.limit]]
        return ListActiveOffersResponse(items=items, total=len(active), limit=request.limit, offset=request.offset)
    
    def StreamOfferUpdates(self, request, context):
        user_id = request.user_id
        q = Queue()
        if user_id not in active_streams:
            active_streams[user_id] = []
        active_streams[user_id].append(q)
        try:
            while context.is_active():
                try:
                    update = q.get(timeout=1)
                    yield OfferUpdate(
                        offer_id=update["offer_id"],
                        event_type=update["event_type"],
                        new_stage=update.get("new_stage", ""),
                        message=update["message"],
                        timestamp=update["timestamp"]
                    )
                except:
                    pass
        finally:
            if user_id in active_streams:
                active_streams[user_id].remove(q)


class GroupServiceServicerImpl(GroupServiceServicer):
    
    def CreateGroup(self, request, context):
        group_id = f"GRP-{uuid.uuid4().hex[:4].upper()}"
        groups[group_id] = {
            "id": group_id,
            "name": request.name,
            "leader_id": request.leader_id,
            "status": "forming",
            "member_ids": [request.leader_id],
            "created_at": datetime.now().isoformat()
        }
        return CreateGroupResponse(group_id=group_id, status="created")
    
    def GetGroup(self, request, context):
        group = groups.get(request.group_id)
        if not group:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return Group()
        return Group(
            id=group["id"],
            name=group["name"],
            leader_id=group["leader_id"],
            status=group["status"],
            member_ids=group["member_ids"],
            created_at=group["created_at"]
        )
    
    def AddMember(self, request, context):
        group = groups.get(request.group_id)
        if not group:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return AddMemberResponse()
        if request.member_id not in group["member_ids"]:
            group["member_ids"].append(request.member_id)
        if len(group["member_ids"]) >= 3 and group["status"] == "forming":
            group["status"] = "ready"
        return AddMemberResponse(group_id=request.group_id, members_count=len(group["member_ids"]))
    
    def ListUserGroups(self, request, context):
        user_groups = [g for g in groups.values() if request.user_id in g["member_ids"]]
        summaries = [GroupSummary(id=g["id"], name=g["name"], status=g["status"], members_count=len(g["member_ids"])) for g in user_groups]
        return ListUserGroupsResponse(groups=summaries)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_RequestServiceServicer_to_server(RequestServiceServicerImpl(), server)
    add_GroupServiceServicer_to_server(GroupServiceServicerImpl(), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC Server запущен на порту 50051")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
        print("Сервер остановлен")

if __name__ == "__main__":
    serve()