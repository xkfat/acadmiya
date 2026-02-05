# In core/admin.py - Make it usable:
from django.contrib import admin
from .models import Departement, Filiere, Module, Inscription, Note

@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'manager']
    search_fields = ['name', 'code']

@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'departement', 'niveau', 'capacity']
    list_filter = ['departement', 'niveau']

@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ['student', 'filiere', 'status', 'created_at']
    list_filter = ['status', 'filiere__departement']
    search_fields = ['student__username', 'student__email']




@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = [
        'student', 
        'module', 
        'academic_year', 
        'note_controle', 
        'note_examen', 
        'note_finale',
        'saisie_par'
    ]
    
    list_filter = [
        'module__filiere__departement',
        'module__filiere',
        'module',
        'academic_year',
        'saisie_par'
    ]
    
    search_fields = [
        'student__username',
        'student__cne',
        'student__first_name',
        'student__last_name',
        'module__code',
        'module__name'
    ]
    
    readonly_fields = ['note_finale', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('student', 'module', 'academic_year')
        }),
        ('Notes', {
            'fields': ('note_controle', 'note_examen', 'note_finale')
        }),
        ('Gouvernance', {
            'fields': ('saisie_par', 'created_at', 'updated_at')
        }),
    )