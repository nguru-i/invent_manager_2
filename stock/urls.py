from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/create/', views.create_loan_view, name='create_loan'),
    path('loans/<int:pk>/return/', views.return_loan_view, name='return_loan'),
    path('loans/export/', views.export_loans_to_excel, name='export_loans'),
]