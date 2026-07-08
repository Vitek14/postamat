from abc import ABC, abstractmethod


class UserNotificationApi(ABC):
    @abstractmethod
    def send_receive_code(self, phone: str, receive_code: str, order_id: str) -> None:
        pass
