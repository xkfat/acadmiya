from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Roles Enum
    ROLE_CHOICES = (
        ('ETUDIANT', 'Étudiant'),
        ('ENSEIGNANT', 'Enseignant'),
        ('ADMIN', 'Administrateur'),
        ('DIRECTION', 'Direction'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ETUDIANT')
    cne = models.CharField(max_length=20, blank=True, null=True, help_text="Pour les étudiants uniquement")
    matricule = models.CharField(max_length=20, blank=True, null=True, help_text="Pour les profs/admins")
    photo = models.ImageField(upload_to='photos_profil/', blank=True, null=True)
    
    # Governance: Who created this user? (Traceability)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"