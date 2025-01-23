from django.contrib import admin
from core_apps.core.models import Transaction, CreditCard

class TransactionAdmin(admin.ModelAdmin):
    list_editable = ['amount', 'status', 'transaction_type', 'receiver', 'sender']
    list_display = ['user', 'amount', 'status', 'transaction_type', 'receiver', 'sender']

class CreditCardAdmin(admin.ModelAdmin):
    list_editable = ['amount', 'card_type']
    list_display = ['user', 'amount', 'card_type']

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(CreditCard, CreditCardAdmin)