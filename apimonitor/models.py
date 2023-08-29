from django.db import models

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=50)
    # Other user-related fields


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    # Other transaction-related fields
