from abc import ABC, abstractmethod

class CreateJobOfferCommand:
    """DTO для команды создания отклика на вакансию"""
    def __init__(self, company: str, position: str, user_id: str):
        self.company = company
        self.position = position
        self.user_id = user_id

class CreateJobOfferUseCase(ABC):
    """Входящий порт: создание отклика"""
    
    @abstractmethod
    def create_offer(self, command: CreateJobOfferCommand) -> str:
        """
        Создаёт отклик и возвращает его ID
        :param command: Данные для создания
        :return: ID созданного отклика
        """
        pass
