
import openpyxl
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer, Product, Loan
from .forms import LoanForm
from .services import create_loan, return_loan


@login_required
def dashboard(request):
    """Display the main dashboard with summary statistics."""
    total_products = Product.objects.count()
    total_customers = Customer.objects.count()
    active_loans = Loan.objects.filter(status=Loan.Status.OUT_ON_LOAN).count()
    low_stock = Product.objects.filter(quantity__lt=3)

    context = {
        'total_products': total_products,
        'total_customers': total_customers,
        'active_loans': active_loans,
        'low_stock': low_stock
    }

    return render(request, 'stock/dashboard.html', context)

@login_required
def loan_list(request):
    """Display all loans."""
    loans = Loan.objects.select_related('customer', 'product').all()

    status_filter = request.GET.get('status')
    if status_filter:
        loans = loans.filter(status=status_filter)

    context = {
        'loans': loans,
        'status_filter': status_filter}
    return render(request, 'stock/loan_list.html', context)

@login_required
def create_loan_view(request):
    """Handle the creation of a new loan."""
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            try:
                create_loan(
                product=form.cleaned_data['product'],
                customer=form.cleaned_data['customer'],
                due_back_date=form.cleaned_data['due_back_date']
                )
                return redirect('loan_list')
            except ValueError as e:
                    form.add_error(None, str(e))
            
    else:
        # show a blank form
        form = LoanForm()

    return render(request, 'stock/create_loan.html', {'form': form})

@login_required
def return_loan_view(request, pk):
     """Handle the return of a loaned product."""
     loan = get_object_or_404(Loan, pk=pk)
     if request.method == 'POST':
         try:
             return_loan(loan)
             return redirect('loan_list')
         except ValueError as e:
            return render(request, 'stock/return_loan.html', {'loan': loan, 'error': str(e)})


     return render(request, 'stock/return_loan.html', {'loan': loan})


@login_required
def export_loans_to_excel(request):
    """Export all loans to an Excel file."""
    loans = Loan.objects.select_related('customer', 'product').all()

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Loans'

    headers = ['ID', 'Customer', 'Product', 'Due Back Date', 'Status']
    sheet.append(headers)

    for loan in loans:
        sheet.append([
            loan.id,
            loan.customer.name,
            loan.product.name,
            loan.due_back_date.strftime('%Y-%m-%d'),
            loan.status
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=loans.xlsx'
    workbook.save(response)
    return response