from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    # Display these fields in the list view
    list_display = ['username', 'email', 'role', 'is_staff']
    
    # Add filters for quick searching (e.g., "Show me all Etudiants")
    list_filter = ['role', 'is_staff', 'is_active']
    
    # Allow editing the new fields in the admin form
    fieldsets = UserAdmin.fieldsets + (
        ('Informations Académiques', {'fields': ('role', 'cne', 'matricule', 'photo')}),
    )
    
    # Allow adding new fields when creating a user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations Académiques', {'fields': ('role', 'cne', 'matricule', 'photo')}),
    )

admin.site.register(User, CustomUserAdmin)