from django import forms
from .models import Loan


class LoanForm(forms.ModelForm):
    """Form for creating and updating loans."""
    class Meta:
        model = Loan
        fields = ['product', 'customer', 'due_back_date']
     