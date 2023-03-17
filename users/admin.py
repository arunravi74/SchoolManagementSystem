from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
            ('Profile Info', {'fields': ('gender','address','user_type')}),
    )
admin.site.register(User,CustomUserAdmin)