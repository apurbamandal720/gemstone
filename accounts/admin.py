from django.contrib import admin
from accounts.models import *

# Register your models here.

@admin.register(Profile)
class ProfileModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_by', 'phone', 'business_name', 'country', 'created_on')

@admin.register(InvitedUser)
class InvitedUserModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_by', 'email', 'created_on')
    search_fields = ['email']
    exclude = ('updated_by', 'created_by')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'supplier_id', 'phone', 'email', 'created_on')
    search_fields = ['name']
    exclude = ('updated_by', 'created_by')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'type', 'ownership_type', 'supplier', 'created_on')
    exclude = ('updated_by', 'created_by')