import pytest
from django.utils import timezone
from django.test.utils import override_settings
from django.contrib.auth.models import User
from datetime import timedelta
from django.test import Client
from django.urls import reverse
from django.db import connection
from stock.models import Product, Customer, Loan
from stock.services import create_loan, return_loan

@pytest.mark.django_db
def test_create_loan_decrements_stock():
    #Arrange
    customer = Customer.objects.create(name="Test User", phone="+447111111111", email="test@test.com")
    product = Product.objects.create(name="Test Product", price=10.00, category="Other", quantity=5)
    due_back_date = timezone.now() + timedelta(days=7)

    #Act
    loan = create_loan(customer, product, due_back_date)

    #Assert
    product.refresh_from_db()
    assert product.quantity == 4
    assert loan.status == Loan.Status.OUT_ON_LOAN


@pytest.mark.django_db
def test_create_loan_raises_when_out_of_stock():
    customer = Customer.objects.create(name="Test User", phone="+447111111111", email="test@test.com")
    product = Product.objects.create(name="Test Product", price=10.00, category="Other", quantity=0)
    due_back_date = timezone.now() + timedelta(days=7)

    with pytest.raises(ValueError) as exc_info:
        create_loan(customer, product, due_back_date)

    assert "out of stock" in str(exc_info.value)


@pytest.mark.django_db
def test_return_loan_increments_stock():
     #Arrange
    customer = Customer.objects.create(name="Test User", phone="+447111111111", email="test@test.com")
    product = Product.objects.create(name="Test Product", price=10.00, category="Other", quantity=1)
    due_back_date = timezone.now() + timedelta(days=7)

    #Act
    loan = create_loan(customer, product, due_back_date)
    return_loan(loan)

    #Assert
    product.refresh_from_db()
    assert product.quantity == 1
    assert loan.status == Loan.Status.RETURNED


@pytest.mark.django_db
def test_return_loan_raises_when_already_returned():
    customer = Customer.objects.create(name="Test User", phone="+447111111111", email="test@test.com")
    product = Product.objects.create(name="Test Product", price=10.00, category="Other", quantity=1)
    due_back_date = timezone.now() + timedelta(days=7)

    loan = create_loan(customer, product, due_back_date)
    return_loan(loan)

    with pytest.raises(ValueError) as exc_info:
        return_loan(loan)

    assert "already been returned" in str(exc_info.value)

@pytest.mark.django_db
def test_customer_str():
    customer = Customer.objects.create(name="Test User", phone="+447111111111", email="test@test.com")
    assert str(customer) == "Test User"


@pytest.mark.django_db
def test_product_str():
    product = Product.objects.create(name="Test Product", price=10.00, category="Other", quantity=5)
    assert str(product) == "Test Product"


@pytest.mark.django_db
def test_loan_str():
    customer = Customer.objects.create(name="Test User", phone="+447111111111", email="test@test.com")
    product = Product.objects.create(name="Test Product", price=10.00, category="Other", quantity=5)
    due_back_date = timezone.now() + timedelta(days=7)
    loan = Loan.objects.create(customer=customer, product=product, due_back_date=due_back_date)
    assert str(loan) == f"Test Product loaned to Test User"


@pytest.mark.django_db
def test_dashboard_returns_200():
    user = User.objects.create_user(username='testuser', password='testpass')
    client = Client()
    client.force_login(user)
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_loan_list_returns_200():
    user = User.objects.create_user(username='testuser', password='testpass')
    client = Client()
    client.force_login(user)
    response = client.get(reverse('loan_list'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_create_loan_view_get_returns_200 ():
    user = User.objects.create_user(username='testuser', password='testpass')
    client = Client()
    client.force_login(user)
    response = client.get(reverse('create_loan'))
    assert response.status_code == 200


@pytest.mark.django_db 
def test_create_loan_view_post_success():
    user = User.objects.create_user(username='testuser', password='testpass')
    client = Client()
    client.force_login(user)  # Log in the user to access the view
    customer = Customer.objects.create(name="Test User", phone="+447111111111", email="test@test.com")
    product = Product.objects.create(name="Test Product", price=10.00, category="Other", quantity=5)
    due_back_date = (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M')

    response = client.post(reverse('create_loan'), {
        'customer': customer.id,
        'product': product.id,
        'due_back_date': due_back_date
    })
    assert response.status_code == 302  # Redirect after successful creation
    assert Loan.objects.count() == 1

@pytest.mark.django_db
def test_create_loan_view_post_out_of_stock ():
    user = User.objects.create_user(username='testuser', password='testpass')
    client = Client()
    client.force_login(user)  # Log in the user to access the view
    customer = Customer.objects.create(name="Test User", phone="+447111111111", email="test@test.com")
    product = Product.objects.create(name="Test Product", price=10.00, category="Other", quantity=0)
    due_back_date = (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M')

    response = client.post(reverse('create_loan'), {
        'customer': customer.id,
        'product': product.id,
        'due_back_date': due_back_date
    })
    assert response.status_code == 200  # Render form with errors
    assert Loan.objects.count() == 0


@pytest.mark.django_db
def test_return_loan_view_post_success():
    user = User.objects.create_user(username='testuser', password='testpass')
    client = Client()
    client.force_login(user)
    customer = Customer.objects.create(name="Test User", phone="+447111111111", email="test@test.com")
    product = Product.objects.create(name="Test Product", price=10.00, category="Other", quantity=5)
    due_back_date = (timezone.now() + timedelta(days=7))
    loan = create_loan(customer, product, due_back_date)

    response = client.post(reverse('return_loan', args=[loan.id]))

    assert response.status_code == 302  # Redirect after successful return
    assert Loan.objects.get(id=loan.id).status == Loan.Status.RETURNED


@pytest.mark.django_db
def test_return_loan_view_already_returned():
    user = User.objects.create_user(username='testuser', password='testpass')
    client = Client()
    client.force_login(user)  # Log in the user to access the view
    customer = Customer.objects.create(name="Test User", phone="+447111111111", email="test@test.com")
    product = Product.objects.create(name="Test Product", price=10.00, category="Other", quantity=5)
    due_back_date = (timezone.now() + timedelta(days=7))
    loan = create_loan(customer, product, due_back_date)
    return_loan(loan)  # return it once directly via service

     # now try to return it again via the view, which should fail
    response = client.post(reverse('return_loan', args=[loan.id]))

    assert response.status_code == 200  # Stay on page and render form with errors
    

@pytest.mark.django_db
def test_return_loan_view_get_returns_200 ():
    user = User.objects.create_user(username='testuser', password='testpass')
    client = Client()
    client.force_login(user)  # Log in the user to access the view
    customer = Customer.objects.create(name="Test User", phone="+447111111111", email="test@test.com")
    product = Product.objects.create(name="Test Product", price=10.00, category="Other", quantity=5)
    due_back_date = (timezone.now() + timedelta(days=7))
    loan = create_loan(customer, product, due_back_date)
    return_loan(loan)  # return it once directly via service

     # now try to return it again via the view, which should fail
    response = client.get(reverse('return_loan', args=[loan.id]))

    assert response.status_code == 200


@pytest.mark.django_db
def test_loan_list_query_count():
    #Arrange --create 3 loans
    user = User.objects.create_user(username='testuser', password='testpass')
    customer = Customer.objects.create(name="Test User", phone="+447111111111", email="test@test.com")
    product = Product.objects.create(name="Test Product", price=10.00, category="Other", quantity=5)
    due_back_date = (timezone.now() + timedelta(days=7))
    create_loan(customer, product, due_back_date)
    create_loan(customer, product, due_back_date)
    create_loan(customer, product, due_back_date)

    #Act -- reset query log, hit the view
    client = Client()
    client.force_login(user)  # Log in the user to access the view
    connection.queries_log.clear()
    with override_settings(DEBUG=True):
        response = client.get(reverse('loan_list'))
        query_count = len(connection.queries)

    #Assert -- # 1 loan query + session/auth queries
    assert response.status_code == 200
    assert query_count <= 4


@pytest.mark.django_db
def test_loan_list_status_filter():
    # Arrange
    user = User.objects.create_user(username='testuser', password='testpass')
    customer = Customer.objects.create(name="Test User", phone="+447111111111", email="test@test.com")
    product = Product.objects.create(name="Test Product", price=10.00, category="Other", quantity=5)
    due_back_date = timezone.now() + timedelta(days=7)
    create_loan(customer, product, due_back_date)  # Out on Loan
    loan2 = create_loan(customer, product, due_back_date)
    return_loan(loan2)  # Returned

    # Act
    client = Client()
    client.force_login(user)
    response = client.get(reverse('loan_list') + '?status=Returned')

    # Assert
    assert response.status_code == 200
    assert len(response.context['loans']) == 1
    assert response.context['loans'][0].status == Loan.Status.RETURNED

@pytest.mark.django_db
def test_export_loans_excel():
    # Arrange
    user = User.objects.create_user(username='testuser', password='testpass')
    customer = Customer.objects.create(name="Test User", phone="+447111111111", email="test@test.com")
    product = Product.objects.create(name="Test Product", price=10.00, category="Other", quantity=5)
    create_loan(customer, product, timezone.now() + timedelta(days=7))

    # Act
    client = Client()
    client.force_login(user)
    response = client.get(reverse('export_loans'))

    # Assert
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'loans.xlsx' in response['Content-Disposition']
