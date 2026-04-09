# grpc/client.py
import grpc
from generated import request_service_pb2, request_service_pb2_grpc

def stream_offers():
    channel = grpc.insecure_channel('localhost:50051')
    stub = request_service_pb2_grpc.RequestServiceStub(channel)
    
    request = request_service_pb2.StreamOfferUpdatesRequest(user_id="USR-001")
    
    print("Подключен к потоку обновлений. Ожидание событий...")
    
    for update in stub.StreamOfferUpdates(request):
        print(f"[{update.timestamp}] {update.event_type}: {update.message}")
        print(f"  Отклик: {update.offer_id}, Этап: {update.new_stage}")

if __name__ == "__main__":
    stream_offers()