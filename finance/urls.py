from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('add/', views.add_transaction, name='add_transaction'),
    path('list/', views.transaction_list, name='transaction_list'),
    path('edit/<int:pk>/', views.edit_transaction, name='edit_transaction'),
    path('delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
]