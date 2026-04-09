class JobOfferService:
    """Реализация use-cases для управления откликами на вакансии"""
    
    def __init__(self, repository, notification_service):
        self.repository = repository
        self.notification_service = notification_service
    
    def create_offer(self, command):
        # TODO: реализовать в Lab #4
        # 1. Создать JobOffer (domain)
        # 2. Сохранить через repository
        # 3. Вернуть ID
        raise NotImplementedError("Будет реализовано в Lab #4")
    
    def get_offer(self, offer_id: str):
        # TODO: реализовать в Lab #4
        # 1. Найти через repository
        # 2. Вернуть domain объект
        raise NotImplementedError("Будет реализовано в Lab #4")
