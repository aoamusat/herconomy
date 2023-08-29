from .models import User, Transaction
from rest_framework import serializers


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "phone")


class TransactionSerializer(serializers.ModelSerializer):
    destination_account = serializers.CharField(max_length=256, source="to")
    amount = serializers.DecimalField(decimal_places=2, max_digits=10)
    narration = serializers.CharField(max_length=256)

    def validate_amount(self, value):
        if value < 50:
            raise serializers.ValidationError("Minimum amount must 50")
        return value

    class Meta:
        model = Transaction
        fields = ("destination_account", "amount", "narration")
