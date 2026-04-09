# application/command/handlers/create_job_offer_handler.py
from datetime import datetime
import uuid

from domain.models.job_offer import JobOffer
from domain.value_objects.company_name import CompanyName
from port.out.job_offer_repository import JobOfferRepository
from port.out.notification_service import NotificationService
from command.create_job_offer_command import CreateJobOfferCommand


class CreateJobOfferHandler:
    def __init__(self, repository: JobOfferRepository, notification_service: NotificationService):
        self._repository = repository
        self._notification_service = notification_service

    def handle(self, command: CreateJobOfferCommand) -> str:
        if not command.company or not command.company.strip():
            raise ValueError("Company name cannot be empty")
        if not command.position or not command.position.strip():
            raise ValueError("Position cannot be empty")
        if not command.user_id or not command.user_id.strip():
            raise ValueError("User ID cannot be empty")

        year = datetime.now().year
        unique_part = uuid.uuid4().hex[:4].upper()
        offer_id = f"OFFER-{year}-{unique_part}"

        company = CompanyName(command.company)

        job_offer = JobOffer(
            offer_id=offer_id,
            company=company,
            position=command.position,
            user_id=command.user_id
        )

        self._repository.save(job_offer)

        for event in job_offer.events:
            self._notification_service.publish(event)
        job_offer.clear_events()

        return offer_id