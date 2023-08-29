from email.policy import default
import random
from typing import Optional
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)

from datetime import timedelta
import uuid
from django.utils import timezone
from apimonitor.exceptions import InvalidTransactionError

# Create your models here.


class UserManager(BaseUserManager):
    def create_user(
        self,
        email: str,
        phone: str,
        first_name: str,
        last_name: str,
        password: Optional[str] = None,
    ):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            phone=phone,
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, first_name, last_name, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    TIER_CHOICES = [
        ("tier1", "Tier 1"),
        ("tier2", "Tier 2"),
        ("tier3", "Tier 3"),
    ]

    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    phone = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)  # type: ignore
    is_superuser = models.BooleanField(default=False)
    flagged = models.BooleanField(default=False)
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    account_number = models.CharField(
        max_length=10, unique=True, default="", editable=False
    )
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default="tier1")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone"]

    def __str__(self) -> str:
        return f"{self.email}"

    def has_perm(self, perm, obj=None) -> bool:
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label) -> bool:
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def custom_is_staff(self) -> bool:
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    @property
    def is_new_user(self) -> bool:
        time_difference = timedelta(days=3)
        return (timezone.now() - self.created_at) <= time_difference

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super(User, self).save(*args, **kwargs)

    def generate_account_number(self):
        prefix = "4"
        random_suffix = str(random.randint(1000000, 9999999))
        return prefix + random_suffix

    @classmethod
    def get_by_account_number(cls, account_number):
        try:
            return cls.objects.get(account_number=account_number)
        except cls.DoesNotExist:
            return None


class Transaction(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipient")
    reference = models.CharField(
        max_length=32, unique=True, null=False, default=uuid.uuid4().hex[:32]
    )
    narration = models.CharField(blank=False, null=False, max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.sender == self.to:
            raise InvalidTransactionError("Source and destination cannot be the same!")
        super(Transaction, self).save(*args, **kwargs)
