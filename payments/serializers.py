from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "order", "user", "amount", "type", "payload", "created_at"]
        read_only_fields = ["user", "created_at"]


