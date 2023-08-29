from .models import User, Transaction
from rest_framework.serializers import ModelSerializer


class AccountSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "phone")


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
