from django.db import models
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+447109901109'. Up to 15 digits allowed."
)

class Customer(models.Model):
    """Model representing a customer."""
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, validators=[phone_validator])
    email = models.EmailField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    """Model representing a product."""
    class Category(models.TextChoices):
        ELECTRONICS = 'Electronics', 'Electronics'
        FURNITURE = 'Furniture', 'Furniture'
        CLOTHING = 'Clothing', 'Clothing'
        INDOOR = 'Indoor', 'Indoor'
        OUTDOOR = 'Outdoor', 'Outdoor'
        OTHER = 'Other', 'Other'
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, choices=Category.choices)
    quantity = models.PositiveIntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Loan(models.Model):
    """Model representing a loan of a product to a customer."""
    class Status(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        OUT_ON_LOAN = 'Out on Loan', 'Out on Loan'
        DUE_BACK = 'Due Back', 'Due Back'
        RETURNED = 'Returned', 'Returned'
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    status = models.CharField(max_length=100, choices=Status.choices)
    loaned_date = models.DateTimeField(auto_now_add=True)
    due_back_date = models.DateTimeField()

    def __str__(self):
        return f"{self.product.name} loaned to {self.customer.name}"