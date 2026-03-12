import logging

from django.db import transaction
from .models import Loan


logger = logging.getLogger(__name__)

@transaction.atomic
def create_loan(customer, product, due_back_date):
    """Service function to create a new loan."""
    if product.quantity > 0:
        product.quantity -= 1
        product.save()
        loan = Loan.objects.create(
            customer=customer,
            product=product,
            due_back_date=due_back_date,
            status=Loan.Status.OUT_ON_LOAN
        )
        logger.info(f"Created loan for {product.name}, id {loan.id}, to {customer.name} ({customer.id}), due back on {due_back_date}.")
    else:
        logger.warning(f"Failed to create loan for {product.name}: Product is out of stock.")
        raise ValueError("Product is out of stock.")
        
    
    return loan

@transaction.atomic
def return_loan(loan):
    """Service function to return a loaned product."""
    if loan.status != Loan.Status.RETURNED:
        loan.status = Loan.Status.RETURNED
        loan.save()
        product = loan.product
        product.quantity += 1
        product.save()
        logger.info(f"Returned loan for {product.name} from {loan.customer.name}.")
    else:
        logger.warning(f"Failed to return loan for {loan.product.name}: Loan has already been returned.")
        raise ValueError("Loan has already been returned.")
    
    return loan