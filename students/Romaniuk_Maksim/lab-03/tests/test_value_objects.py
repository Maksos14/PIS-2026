import pytest
from datetime import datetime, timedelta

from domain.value_objects.company_name import CompanyName
from domain.value_objects.stage_type import StageType
from domain.value_objects.offer_status import OfferStatus
from domain.value_objects.reminder_time import ReminderTime


class TestCompanyName:
    
    def test_should_create_valid_company_name(self):
        name = CompanyName("ООО Яндекс")
        assert name.value == "ООО Яндекс"
    
    def test_should_trim_whitespace(self):
        name = CompanyName("  Google  ")
        assert name.value == "Google"
    
    def test_short_name_should_truncate_long_names(self):
        long_name = "Very Long Company Name That Exceeds Twenty Characters"
        name = CompanyName(long_name)
        assert len(name.short_name) <= 20
    
    def test_should_detect_contained_text(self):
        name = CompanyName("Microsoft Corporation")
        assert name.contains("soft") is True
        assert name.contains("Apple") is False


class TestStageType:
    
    def test_should_have_correct_order(self):
        assert StageType.resume_sent().order == 0
        assert StageType.hr_screening().order == 1
        assert StageType.tech_interview().order == 2
        assert StageType.test_task().order == 3
        assert StageType.final_interview().order == 4
        assert StageType.offer().order == 5
    
    def test_should_allow_transition_to_next_stage(self):
        current = StageType.resume_sent()
        next_stage = StageType.hr_screening()
        assert current.can_transition_to(next_stage) is True
    
    def test_should_not_allow_skip_stages(self):
        current = StageType.resume_sent()
        skip = StageType.tech_interview()
        assert current.can_transition_to(skip) is False
    
    def test_should_not_allow_backward_transition(self):
        current = StageType.hr_screening()
        previous = StageType.resume_sent()
        assert current.can_transition_to(previous) is False
    
    def test_should_identify_first_stage(self):
        assert StageType.resume_sent().is_first is True
        assert StageType.hr_screening().is_first is False
    
    def test_should_identify_last_stage(self):
        assert StageType.offer().is_last is True
        assert StageType.final_interview().is_last is False


class TestOfferStatus:
    
    def test_should_create_active_status(self):
        status = OfferStatus.active()
        assert status.is_active is True
        assert status.is_rejected is False
        assert status.is_offer_received is False
        assert status.can_change_stage() is True
    
    def test_should_create_rejected_status(self):
        status = OfferStatus.rejected()
        assert status.is_active is False
        assert status.is_rejected is True
        assert status.is_offer_received is False
        assert status.can_change_stage() is False
    
    def test_should_create_offer_received_status(self):
        status = OfferStatus.offer_received()
        assert status.is_active is False
        assert status.is_rejected is False
        assert status.is_offer_received is True
        assert status.can_change_stage() is False


class TestReminderTime:
    
    def test_should_create_future_reminder(self):
        future = datetime.now() + timedelta(days=1)
        reminder = ReminderTime(future)
        assert reminder.value == future
    
    def test_should_not_create_past_reminder(self):
        past = datetime.now() - timedelta(days=1)
        with pytest.raises(ValueError, match="cannot be in the past"):
            ReminderTime(past)
    
    def test_should_detect_urgent_reminder(self):
        soon = datetime.now() + timedelta(minutes=30)
        reminder = ReminderTime(soon)
        assert reminder.is_urgent(60) is True
    
    def test_should_format_relative_time(self):
        tomorrow = datetime.now() + timedelta(days=1)
        reminder = ReminderTime(tomorrow)
        assert "через" in reminder.format_relative()
    
    def test_should_create_from_iso_string(self):
        # Используем будущую дату, чтобы не было ошибки "in the past"
        future_date = datetime.now() + timedelta(days=30)
        iso_string = future_date.strftime("%Y-%m-%dT%H:%M:%S")
        reminder = ReminderTime.from_iso(iso_string)
        assert reminder.year == future_date.year
        assert reminder.month == future_date.month
        assert reminder.day == future_date.day