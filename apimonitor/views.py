import datetime
from apimonitor.serializers import TransactionSerializer
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apimonitor.auth import HerconomyAPIAuthentication
from django.core.cache import cache
from apimonitor.utils import (
    call_webhook,
    resolve_account,
    generate_transaction_reference,
)
from django.contrib.auth import get_user_model
from apimonitor.models import Transaction
from django.utils import timezone
from django.conf import settings
from apimonitor.exceptions import InvalidTransactionError


prefix = "THROTTLE_"

User = get_user_model()

# Create your views here.
class IndexView(APIView):
    def get(self, request):
        data = {
            "service": "Herconomy API Monitor",
            "version": "1.0",
        }

        return JsonResponse(data=data, status=status.HTTP_200_OK)


class TransactionView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [HerconomyAPIAuthentication]

    def post(self, request):
        payload = {
            "amount": request.data.get("amount"),
            "destination_account": request.data.get("destination_account"),
            "narration": request.data.get("narration"),
        }

        serializer = TransactionSerializer(data=payload)

        # validate input
        if serializer.is_valid():
            # Resolve destination account
            recipient = resolve_account(f"{payload.get('destination_account')}")
            sender = request.user
            if recipient is None:
                return JsonResponse(
                    data={"message": "Account not found!"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Policy: Transaction amount exceeds the amount for a given tier.
            sender_tier = str(sender.tier)
            tier_amount = settings.ACCOUNT_LIMITS[sender_tier]

            if payload.get("amount") > tier_amount:
                webhook_payload = {
                    "event": "account.tier.exceeded",
                    "source_account": request.user.account_number,
                    "amount": payload.get("amount"),
                }
                call_webhook(settings.WEBHOOK_URL, webhook_payload)

            # Policy: The transaction amount is greater than 5,000,000
            if payload.get("amount") > 5000000:
                webhook_payload = {
                    "event": "transaction.large",
                    "destination_account": recipient.account_number,
                    "source_account": request.user.account_number,
                    "amount": payload.get("amount"),
                }
                call_webhook(settings.WEBHOOK_URL, webhook_payload)

            # Policy: Transaction is happening between a regular user and previously flagged user
            if recipient.flagged or sender.flagged:
                webhook_payload = {
                    "event": "transaction.suspicious",
                    "destination_account": recipient.account_number,
                    "source_account": request.user.account_number,
                }
                call_webhook(settings.WEBHOOK_URL, webhook_payload)

            # Policy: Transaction is attributed to a new user
            if recipient.is_new_user or sender.is_new_user:
                webhook_payload = {
                    "event": "newuser.transaction",
                    "destination_account": recipient.account_number,
                    "source_account": request.user.account_number,
                    "amount": payload.get("amount"),
                }
                call_webhook(settings.WEBHOOK_URL, webhook_payload)

            # Policy: Transaction from a particular user occurs within a timing window of less than 1 minute
            sender_recent_transactions = Transaction.objects.filter(
                sender=sender,
                created_at__gte=timezone.now() - datetime.timedelta(minutes=1),
            )
            if sender_recent_transactions.exists():
                call_webhook(settings.WEBHOOK_URL, webhook_payload)

            try:
                tx = Transaction(
                    amount=payload.get("amount"),
                    sender=sender,
                    to=recipient,
                    reference=generate_transaction_reference(),
                )

                recipient.account_balance += payload.get("amount")
                recipient.save()
                tx.save()
                return JsonResponse(
                    data={
                        "source_account": sender.account_number,
                        "source_name": f"{sender.first_name} {sender.last_name}",
                        "destination_name": f"{recipient.first_name} {recipient.last_name}",
                        "destination_account": recipient.account_number,
                        "tx_reference": tx.reference,
                    },
                    status=status.HTTP_200_OK,
                )
            except InvalidTransactionError as e:
                return JsonResponse(
                    data={"message": e.message}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return JsonResponse(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
