from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import TransactionForm
from .models import Transaction, Category

def home(request):
    return render(request, 'finance/home.html')

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'finance/add_transaction.html', {'form': form})

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    category_id = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if category_id:
        transactions = transactions.filter(category_id=category_id)
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)

    income = sum(t.amount for t in transactions if t.type == 'income')
    expenses = sum(t.amount for t in transactions if t.type == 'expense')
    balance = income - expenses

    context = {
        'transactions': transactions,
        'income': income,
        'expenses': expenses,
        'balance': balance,
        'categories': Category.objects.all(),
    }
    return render(request, 'finance/transaction_list.html', context)

@login_required
def edit_transaction(request, pk):
    txn = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=txn)
        if form.is_valid():
            form.save()
            messages.success(request, 'Транзакция обновлена.')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=txn)
    return render(request, 'finance/edit_transaction.html', {'form': form, 'txn': txn})

@login_required
def delete_transaction(request, pk):
    txn = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        txn.delete()
        messages.success(request, 'Транзакция удалена.')
        return redirect('transaction_list')
    return render(request, 'finance/confirm_delete.html', {'txn': txn})
