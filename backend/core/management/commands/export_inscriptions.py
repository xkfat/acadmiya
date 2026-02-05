"""
Management command to export inscriptions to CSV
Usage: python manage.py export_inscriptions [--status PENDING] [--output inscriptions.csv]
"""
from django.core.management.base import BaseCommand
from core.models import Inscription
import csv
from django.utils import timezone


class Command(BaseCommand):
    help = 'Export inscriptions to CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--status',
            type=str,
            help='Filter by status (PENDING, VALIDATED, REJECTED)',
        )
        parser.add_argument(
            '--output',
            type=str,
            default=f'inscriptions_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv',
            help='Output CSV filename',
        )
        parser.add_argument(
            '--filiere',
            type=int,
            help='Filter by filiere ID',
        )

    def handle(self, *args, **options):
        # Build queryset
        inscriptions = Inscription.objects.select_related(
            'student', 'filiere', 'filiere__departement', 'validated_by'
        ).all()

        # Apply filters
        if options['status']:
            inscriptions = inscriptions.filter(status=options['status'])
        
        if options['filiere']:
            inscriptions = inscriptions.filter(filiere_id=options['filiere'])

        # Create CSV
        output_file = options['output']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'ID',
                'Étudiant (CNE)',
                'Nom Complet',
                'Email',
                'Filière',
                'Département',
                'Année Académique',
                'Statut',
                'Date Candidature',
                'Validé par',
                'Date Validation',
                'Motif Rejet'
            ])
            
            # Data rows
            for inscription in inscriptions:
                writer.writerow([
                    inscription.id,
                    inscription.student.cne or 'N/A',
                    f"{inscription.student.first_name} {inscription.student.last_name}",
                    inscription.student.email,
                    inscription.filiere.name,
                    inscription.filiere.departement.name,
                    inscription.academic_year,
                    inscription.status,
                    inscription.created_at.strftime('%Y-%m-%d %H:%M'),
                    inscription.validated_by.username if inscription.validated_by else 'N/A',
                    inscription.validation_date.strftime('%Y-%m-%d %H:%M') if inscription.validation_date else 'N/A',
                    inscription.rejection_reason or 'N/A'
                ])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Exported {inscriptions.count()} inscriptions to {output_file}'
            )
        )