from django.contrib import admin
from .models import Departement, Filiere, Module, Inscription

# ============================================
# DEPARTEMENT ADMIN
# ============================================
@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'manager', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'code']
    ordering = ['name']
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('name', 'code', 'description')
        }),
        ('Gouvernance', {
            'fields': ('manager',)
        }),
    )


# ============================================
# FILIERE ADMIN
# ============================================
@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'departement', 'niveau', 'capacity', 'created_at']
    list_filter = ['departement', 'niveau', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['departement', 'name']
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('name', 'code', 'departement', 'niveau')
        }),
        ('Détails Académiques', {
            'fields': ('capacity', 'description')
        }),
    )


# ============================================
# MODULE ADMIN
# ============================================
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'filiere', 'enseignant', 'semestre', 'coefficient']
    list_filter = ['filiere__departement', 'filiere', 'semestre', 'created_at']
    search_fields = ['name', 'code', 'enseignant__username']
    ordering = ['filiere', 'semestre', 'name']
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('name', 'code', 'filiere', 'enseignant')
        }),
        ('Détails Académiques', {
            'fields': ('semestre', 'coefficient', 'heures_cm', 'heures_td', 'heures_tp', 'description')
        }),
    )


# ============================================
# INSCRIPTION ADMIN (GOVERNANCE CRITICAL)
# ============================================
@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'student', 
        'filiere', 
        'academic_year', 
        'status', 
        'validated_by', 
        'created_at'
    ]
    
    list_filter = [
        'status', 
        'academic_year', 
        'filiere__departement', 
        'filiere',
        'created_at'
    ]
    
    search_fields = [
        'student__username', 
        'student__email', 
        'student__cne',
        'filiere__name'
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Inscription', {
            'fields': ('student', 'filiere', 'academic_year')
        }),
        ('Gouvernance', {
            'fields': ('status', 'validated_by', 'validation_date', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Actions: Bulk validate/reject
    actions = ['validate_inscriptions', 'reject_inscriptions']
    
    def validate_inscriptions(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status='VALIDATED',
            validated_by=request.user,
            validation_date=timezone.now()
        )
        self.message_user(request, f"{updated} inscription(s) validée(s).")
    validate_inscriptions.short_description = "✅ Valider les inscriptions sélectionnées"
    
    def reject_inscriptions(self, request, queryset):
        updated = queryset.update(status='REJECTED', validated_by=request.user)
        self.message_user(request, f"{updated} inscription(s) rejetée(s).")
    reject_inscriptions.short_description = "❌ Rejeter les inscriptions sélectionnées"