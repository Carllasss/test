class ServiceError(Exception):
    """Базовая ошибк"""


class UserAlreadyExists(ServiceError):
    """Пользователь с таким telegram_id уже существует"""

    def __init__(self, telegram_id: int):
        super().__init__(f"User with telegram_id={telegram_id} already exists")
        self.telegram_id = telegram_id

