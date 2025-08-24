from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.functions import TruncMonth
from django.db.models import Sum

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

@login_required
def report_view(request):
    transactions = Transaction.objects.filter(user=request.user)

    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    balance = total_income - total_expense

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
    }
    return render(request, 'finance/report.html', context)

@login_required
def report(request):
    transactions = Transaction.objects.filter(user=request.user)

    total_income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    # Группировка по месяцам
    monthly_data = transactions.annotate(month=TruncMonth('date')).values('month', 'type').annotate(
        total=Sum('amount')
    ).order_by('month')

    # Подготавливаем данные для графика
    months = []
    incomes = []
    expenses = []

    for entry in monthly_data:
        month_str = entry['month'].strftime("%Y-%m")
        if month_str not in months:
            months.append(month_str)
            incomes.append(0)
            expenses.append(0)
        index = months.index(month_str)
        if entry['type'] == 'income':
            incomes[index] = float(entry['total'])
        else:
            expenses[index] = float(entry['total'])

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'months': months,
        'incomes': incomes,
        'expenses': expenses,
    }
    return render(request, 'report.html', context)