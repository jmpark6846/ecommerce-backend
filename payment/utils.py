class PaymentService:

    @staticmethod
    def proceed_payment(email, amount, payment_method, mock_failed=False):
        """
        실제 PG사 혹은 결제 서비스 이용해 결제 요청 발송
        """
        if mock_failed:
            raise PaymentError('결제에 실패했습니다.', data={"detail": "결제 사유"})


class PaymentError(Exception):
    def __init__(self, message, data):
        self.message = message
        self.data = data
