from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, APICredit

# Register your models here.
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username', 'current_credit_balance']

class APICreditAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'user', 'amount', 'description' ]

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(APICredit, APICreditAdmin)