from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from stock.models import Customer, Product, Loan
from stock.services import create_loan


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # Clear existing data
        Loan.objects.all().delete()
        Product.objects.all().delete()
        Customer.objects.all().delete()

        # Create customers
        alice = Customer.objects.create(name="Alice Smith", phone="+447700900001", email="alice@example.com")
        bob = Customer.objects.create(name="Bob Jones", phone="+447700900002", email="bob@example.com")
        carol = Customer.objects.create(name="Carol White", phone="+447700900003", email="carol@example.com")

        # Create products
        chair = Product.objects.create(name="Folding Chair", price=15.00, category="Furniture", quantity=10)
        drill = Product.objects.create(name="Power Drill", price=45.00, category="Electronics", quantity=3)
        tent = Product.objects.create(name="Garden Tent", price=80.00, category="Outdoor", quantity=2)
        lamp = Product.objects.create(name="Desk Lamp", price=20.00, category="Electronics", quantity=0, is_active=False)

        # Create loans
        create_loan(alice, chair, timezone.now() + timedelta(days=7))
        create_loan(bob, drill, timezone.now() + timedelta(days=14))
        loan = create_loan(carol, tent, timezone.now() + timedelta(days=3))

        # Return one loan
        from stock.services import return_loan
        return_loan(loan)

        self.stdout.write(self.style.SUCCESS('Done. 3 customers, 4 products, 3 loans (1 returned).'))
