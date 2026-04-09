from abc import ABC, abstractmethod

class GetJobOfferUseCase(ABC):
    """Входящий порт: получение отклика по ID"""
    
    @abstractmethod
    def get_offer(self, offer_id: str):
        """
        Получает отклик по ID
        :param offer_id: Идентификатор отклика
        :return: Объект JobOffer или None
        """
        pass
