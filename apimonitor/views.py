from datetime import datetime
from apimonitor.serializers import TransactionSerializer
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apimonitor.auth import MessageRequestThrotlle, HerconomyAPIAuthentication
from django.core.cache import cache

prefix = "THROTTLE_"

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
            "to": request.data.get("to"),
            "text": request.data.get("text"),
        }

        pass
