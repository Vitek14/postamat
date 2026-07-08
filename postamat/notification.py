from .interfaces import UserNotificationApi


class NotificationClient(UserNotificationApi):
    def send_receive_code(self, phone: str, receive_code: str, order_id: str) -> None:
        print(f"SMS to {phone}: code {receive_code} for order {order_id}")
