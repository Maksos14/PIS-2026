## Таблица инвариантов агрегата JobOffer

| Инвариант | Проверка | Где выполняется | Исключение |
|-----------|----------|-----------------|------------|
| Нельзя создать отклик без названия компании | `if not company or not company.strip()` | `CompanyName.__post_init__()` | `ValueError("Company name cannot be empty")` |
| Название компании должно быть от 2 до 100 символов | `if len(stripped) < 2 or len(stripped) > 100` | `CompanyName.__post_init__()` | `ValueError("Company name too short/long")` |
| Должность не может быть пустой | `if not position or not position.strip()` | `JobOffer.__init__()` | `ValueError("Position cannot be empty")` |
| Должность не может быть длиннее 200 символов | `if len(position) > 200` | `JobOffer.__init__()` | `ValueError("Position too long")` |
| User ID не может быть пустым | `if not user_id` | `JobOffer.__init__()` | `ValueError("User ID cannot be empty")` |
| ID отклика должен соответствовать формату OFFER-YYYY-NNNN | `if not re.match(r'OFFER-\d{4}-\d{4}', offer_id)` | `JobOffer.__init__()` | `ValueError("Invalid offer ID format")` |
| Нельзя изменить отклонённый отклик | `if self._status.is_rejected` | `JobOffer._ensure_editable()` | `ValueError("Cannot modify rejected offer")` |
| Нельзя изменить отклик с полученным офером | `if self._status.is_offer_received` | `JobOffer._ensure_editable()` | `ValueError("Cannot modify completed offer")` |
| Нельзя перейти на предыдущий этап | `if new_index < current_index` | `JobOffer.change_stage()` | `ValueError("Cannot go back to previous stage")` |
| Нельзя пропускать этапы | `if new_index > current_index + 1` | `JobOffer.change_stage()` | `ValueError("Cannot skip stages")` |
| Нельзя менять этап у отклонённого отклика | проверка через `_ensure_editable()` | `JobOffer.change_stage()` | `ValueError("Cannot modify rejected offer")` |
| Нельзя отклонить отклик с полученным офером | `if self._status.is_offer_received` | `JobOffer.mark_rejected()` | `ValueError("Cannot reject offer with received offer")` |
| Нельзя отклонить уже отклонённый отклик | `if self._status.is_rejected` | `JobOffer.mark_rejected()` | `ValueError("Offer already rejected")` |
| Заметка не может быть пустой | `if not content or not content.strip()` | `JobOffer.add_note()` | `ValueError("Note cannot be empty")` |
| Заметка не может быть длиннее 1000 символов | `if len(content) > 1000` | `JobOffer.add_note()` | `ValueError("Note too long")` |
| Нельзя добавлять заметки к отклонённому отклику | проверка через `_ensure_editable()` | `JobOffer.add_note()` | `ValueError("Cannot modify rejected offer")` |
| При переходе на этап OFFER статус автоматически меняется | `if new_stage.value == StageTypeEnum.OFFER` | `JobOffer.change_stage()` | автоматическое изменение |
| Прогресс должен быть в диапазоне 0-100% | `(current_index / total_stages) * 100` | `JobOffer.progress_percentage` | гарантирован формулой |
| Статус отклика должен быть одним из допустимых | `if not isinstance(value, OfferStatusEnum)` | `OfferStatus.__post_init__()` | `ValueError("Invalid offer status")` |
| Тип этапа должен быть одним из допустимых | `if not isinstance(value, StageTypeEnum)` | `StageType.__post_init__()` | `ValueError("Invalid stage type")` |