from django.core.management.base import BaseCommand
from apimonitor.models import User, Transaction
from faker import Faker
import random
import decimal


class Command(BaseCommand):
    help = "Seed the users and transactions tables with initial data"

    def handle(self, *args, **options):
        fake = Faker()
        tiers = [choice[0] for choice in User.TIER_CHOICES]

        # Seed Users
        users = []
        for _ in range(10):
            user = User(
                email=fake.email(),
                account_balance=decimal.Decimal(random.uniform(100, 500000)),
                tier=random.choice(tiers),
            )
            users.append(user)
        User.objects.bulk_create(users)

        # Seed Transactions
        transactions = []
        for user in User.objects.all():
            for _ in range(random.randint(0, 20)):
                recipient = random.choice(User.objects.exclude(pk=user.pk))
                transaction = Transaction(
                    amount=decimal.Decimal(random.uniform(1000, 200000)),
                    sender=user,
                    to=recipient,
                    narration=fake.sentence(),
                )
                transactions.append(transaction)
        Transaction.objects.bulk_create(transactions)

        self.stdout.write(self.style.SUCCESS("Database seeded successfully"))
