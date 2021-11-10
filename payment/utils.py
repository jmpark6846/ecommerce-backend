import rest_framework.exceptions
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class PaymentService:

    @staticmethod
    def proceed_payment(email, amount, payment_method, mock_fail=False):
        """
        실제 PG사 혹은 결제 서비스 이용해 결제 요청 발송
        """

        if mock_fail:
            raise PaymentError(detail={"error_msg": "실패 사유"})


class PaymentError(APIException):
    status_code = 500
    default_detail = _('결제를 실패하였습니다.')
