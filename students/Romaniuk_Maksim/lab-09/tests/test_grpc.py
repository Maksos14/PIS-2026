import sys
from pathlib import Path

# Добавляем путь к generated
sys.path.insert(0, str(Path(__file__).parent.parent / "grpc_proto" / "generated"))

import grpc
from grpc.generated.request_service_pb2 import CreateOfferRequest, GetOfferRequest, ChangeStageRequest
from grpc.generated.request_service_pb2_grpc import RequestServiceStub


def run_tests():
    channel = grpc.insecure_channel('localhost:50051')
    stub = RequestServiceStub(channel)
    
    print("1. Создание отклика...")
    resp = stub.CreateOffer(CreateOfferRequest(
        company="Google",
        position="Python Dev",
        user_id="USR-001"
    ))
    print(f"   ✅ Создан: {resp.offer_id}")
    
    print("2. Получение отклика...")
    offer = stub.GetOffer(GetOfferRequest(offer_id=resp.offer_id))
    print(f"   ✅ {offer.company} - {offer.position}")
    
    print("3. Смена этапа...")
    resp2 = stub.ChangeStage(ChangeStageRequest(
        offer_id=resp.offer_id,
        new_stage="hr_screening"
    ))
    print(f"   ✅ {resp2.old_stage} -> {resp2.new_stage}")
    
    print("\n✅ Все тесты пройдены!")
    channel.close()


if __name__ == "__main__":
    run_tests()