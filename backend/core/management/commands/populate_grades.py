import random
from django.core.management.base import BaseCommand
from core.models import Inscription, Module, Note

class Command(BaseCommand):
    help = 'Génère des notes réalistes pour les étudiants validés'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("🚀 Démarrage de la génération des notes..."))

        # 1. Get VALIDATED students
        inscriptions = Inscription.objects.filter(status='VALIDATED')
        
        if not inscriptions.exists():
            self.stdout.write(self.style.ERROR("❌ ERREUR : Aucune inscription validée trouvée."))
            self.stdout.write(self.style.MIGRATE_HEADING("👉 Allez dans l'Espace Admin > Validations et validez des dossiers d'abord."))
            return

        count = 0
        updated = 0

        self.stdout.write(f"ℹ️  Traitement de {inscriptions.count()} étudiants...")

        for inscription in inscriptions:
            student = inscription.student
            filiere = inscription.filiere
            academic_year = inscription.academic_year
            
            # Get modules for this student's filiere
            modules = Module.objects.filter(filiere=filiere)
            
            if not modules.exists():
                continue

            # Randomize profile: 
            # >0.3 = Average (10-14) | > 0.1 = Struggling (4-9) | < 0.1 = Genius (15-19)
            roll = random.random()
            
            for module in modules:
                # Generate realistic grades
                if roll > 0.3: 
                    cc = random.uniform(10, 14.5)
                    exam = random.uniform(9.5, 15)
                elif roll > 0.1:
                    cc = random.uniform(4, 9.5)
                    exam = random.uniform(3, 9)
                else:
                    cc = random.uniform(15, 18)
                    exam = random.uniform(16, 19.5)

                # Save Note
                # note_finale is auto-calculated by the model save() method
                note, created = Note.objects.update_or_create(
                    student=student,
                    module=module,
                    academic_year=academic_year,
                    defaults={
                        'note_controle': round(cc, 2),
                        'note_examen': round(exam, 2)
                    }
                )
                note.save() 
                
                if created:
                    count += 1
                else:
                    updated += 1

        self.stdout.write(self.style.SUCCESS(f"✅ SUCCÈS : {count} notes créées | {updated} mises à jour"))