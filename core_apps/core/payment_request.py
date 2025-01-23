from django.shortcuts import render, redirect
from core_apps.account.models import Account, KYC
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from core_apps.core.models import Transaction


@login_required
def SearchUsersRequest(request):
    """Search user by account nummber or id"""
    account = Account.objects.all()
    query = request.POST.get("account_number")

    kyc = KYC.objects.get(user=request.user)

    if query:
        account = account.filter(
            Q(account_number=query)|
            Q(account_id=query)
        ).distinct()
    
    context = {
        "account": account,
        "query": query,
        "kyc": kyc,
    }
    return render(request, "payment_request/search-users.html", context)

def AmountRequest(request, account_number):
    account = Account.objects.get(account_number=account_number)

    kyc = KYC.objects.get(user=request.user)

    context = {
        "account": account,
        "kyc": kyc,
    }
    return render(request, "payment_request/amount-request.html", context)

def AmountRequestProcess(request, account_number):
    account = Account.objects.get(account_number=account_number)

    sender = request.user
    receiver = account.user

    sender_account = request.user.account
    receiver_account = account

    if request.method == "POST":
        amount = request.POST.get("amount-request")
        description = request.POST.get("description")

        new_request = Transaction.objects.create(
            user=request.user,
            amount=amount,
            description=description,

            sender=sender,
            receiver=receiver,

            sender_account=sender_account,
            receiver_account=receiver_account,

            status="request_processing",
            transaction_type="request",
        )
        new_request.save()
        transaction_id = new_request.transaction_id
        return redirect("core_apps.core:amount-request-confirmation", account.account_number, transaction_id)
    else:
        messages.warning(request, "Error Occured, Try again later.")
        return redirect("core_apps.account:dashboard")

def AmountRequestConfirmation(request, account_number, transaction_id):
    account = Account.objects.get(account_number=account_number)
    transaction = Transaction.objects.get(transaction_id=transaction_id)
    context = {
        "account":account,
        "transaction":transaction
    }
    return render(request, "payment_request/amount-request-confirmation.html", context)


def AmountRequestFinalProcess(request, account_number, transaction_id):
    account = Account.objects.get(account_number=account_number)
    transaction = Transaction.objects.get(transaction_id=transaction_id)

    if request.method == "POST":
        pin_number = request.POST.get("pin-number")
        if pin_number == request.user.account.pin_number:
            transaction.status = "request_sent"
            transaction.save()

            messages.success(request, "Your payment request have been sent successfully.")
            return redirect("core_apps.core:amount-request-completed", account.account_number, transaction.transaction_id)
        else:
            messages.warning(request, "An Error Occurred, Try again later.")
            return redirect("account.dashboard")
    
def RequestCompleted(request, account_number, transaction_id):
    account = Account.objects.get(account_number=account_number)
    transaction = Transaction.objects.get(transaction_id=transaction_id)
    context = {
        "account":account,
        "transaction":transaction
    }
    return render(request, "payment_request/amount-request-completed.html", context)


def settlement_confirmation(request, account_number, transaction_id):
    account = Account.objects.get(account_number=account_number)
    transaction = Transaction.objects.get(transaction_id=transaction_id)
    context = {
        "account":account,
        "transaction":transaction,
    }
    return render(request, "payment_request/settlement-confirmation.html", context)


def settlement_processing(request, account_number, transaction_id):
    account = Account.objects.get(account_number=account_number)
    transaction = Transaction.objects.get(transaction_id=transaction_id)

    sender = request.user
    sender_account = request.user.account

    if request.method == "POST":
        pin_number = request.POST.get("pin-number")
        if pin_number == request.user.account.pin_number:
            if sender_account.account_balance <= 0 or sender_account.account_balance < transaction.amount:
                messages.warning(request, "Insufficient Funds, fund your account and try again.")
            else:
                sender_account.account_balance -= transaction.amount
                sender_account.save()

                account.account_balance += transaction.amount
                account.save()

                transaction.status = "request_settled"
                transaction.save()

                messages.success(request, f"Settled to {account.user.kyc.full_name} was successfull.")
                return redirect("core_apps.core:settlement-completed", account.account_number, transaction.transaction_id)
        else:
            messages.warning(request, "Incorrect Pin")
            return redirect("core_apps.core:settlement-confirmation", account.account_number, transaction.transaction_id)
    else:
        messages.warning(request, "Error Occured")
        return redirect("core_apps.account:dashboard")


def SettlementCompleted(request, account_number, transaction_id):
    account = Account.objects.get(account_number=account_number)
    transaction = Transaction.objects.get(transaction_id=transaction_id)
    context = {
        "account":account,
        "transaction":transaction,
    }
    return render(request, "payment_request/settlement-completed.html", context)

def DeletePaymentRequest(request, account_number, transaction_id):
    account = Account.objects.get(account_number=account_number)
    transaction = Transaction.objects.get(transaction_id=transaction_id)

    if request.user == transaction.user:
        transaction.delete()
        messages.success(request, "Payment Request Deleted Successfully.")
        return redirect("core_apps.core:transactions")