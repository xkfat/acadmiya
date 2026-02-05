from django.db import models
from django.conf import settings

# ============================================
# DEPARTEMENT MODEL
# ============================================
class Departement(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Nom du Département")
    code = models.CharField(max_length=10, unique=True, verbose_name="Code (ex: INFO, GC)")
    description = models.TextField(blank=True, null=True)
    
    # Governance: Who manages this department?
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'ADMIN'},
        related_name='managed_departments',
        verbose_name="Chef de Département"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


# ============================================
# FILIERE MODEL
# ============================================
class Filiere(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom de la Filière")
    code = models.CharField(max_length=10, verbose_name="Code (ex: GI, RT)")
    
    # Relationship: Filiere belongs to Departement
    departement = models.ForeignKey(
        Departement,
        on_delete=models.CASCADE,
        related_name='filieres',
        verbose_name="Département"
    )
    
    # Academic Info
    niveau = models.CharField(
        max_length=50,
        choices=[
            ('LICENSE', 'Licence'),
            ('MASTER', 'Master'),
            ('DOCTORAT', 'Doctorat'),
        ],
        default='LICENSE'
    )
    
    capacity = models.PositiveIntegerField(default=30, verbose_name="Capacité d'accueil")
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Filière"
        verbose_name_plural = "Filières"
        ordering = ['departement', 'name']
        unique_together = ['code', 'departement']  # Same code can exist in different depts
    
    def __str__(self):
        return f"{self.code} - {self.name} ({self.departement.code})"


# ============================================
# MODULE MODEL
# ============================================
class Module(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom du Module")
    code = models.CharField(max_length=20, verbose_name="Code Module")
    
    # Relationship: Module belongs to Filiere
    filiere = models.ForeignKey(
        Filiere,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name="Filière"
    )
    
    # Governance: Who teaches this module?
    enseignant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'ENSEIGNANT'},
        related_name='modules_enseignes',
        verbose_name="Enseignant Responsable"
    )
    
    # Academic Info
    semestre = models.IntegerField(
        choices=[(i, f"S{i}") for i in range(1, 7)],
        default=1,
        verbose_name="Semestre"
    )
    coefficient = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    heures_cm = models.PositiveIntegerField(default=0, verbose_name="Heures CM")
    heures_td = models.PositiveIntegerField(default=0, verbose_name="Heures TD")
    heures_tp = models.PositiveIntegerField(default=0, verbose_name="Heures TP")
    
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"
        ordering = ['filiere', 'semestre', 'name']
        unique_together = ['code', 'filiere']
    
    def __str__(self):
        return f"{self.code} - {self.name} (S{self.semestre})"


# ============================================
# INSCRIPTION MODEL (GOVERNANCE CRITICAL)
# ============================================
class Inscription(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En Attente'),
        ('VALIDATED', 'Validée'),
        ('REJECTED', 'Rejetée'),
    ]
    
    # Who is enrolling?
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'ETUDIANT'},
        related_name='inscriptions',
        verbose_name="Étudiant"
    )
    
    # Enrolling in which program?
    filiere = models.ForeignKey(
        Filiere,
        on_delete=models.CASCADE,
        related_name='inscriptions',
        verbose_name="Filière"
    )
    
    # Academic Year
    academic_year = models.CharField(
        max_length=9,
        verbose_name="Année Universitaire",
        help_text="Format: 2024-2025"
    )
    
    # GOVERNANCE: Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Statut"
    )
    
    # GOVERNANCE: Who validated/rejected this?
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'ADMIN'},
        related_name='inscriptions_validees',
        verbose_name="Validé par"
    )
    
    validation_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="Motif de rejet")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de demande")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        ordering = ['-created_at']
        unique_together = ['student', 'filiere', 'academic_year']  # One inscription per year
    
    def __str__(self):
        return f"{self.student.username} → {self.filiere.code} ({self.academic_year}) [{self.status}]"