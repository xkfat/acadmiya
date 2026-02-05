"""
Management command to clean old pending inscriptions
Usage: python manage.py clean_old_inscriptions [--days 30] [--dry-run]
"""
from django.core.management.base import BaseCommand
from core.models import Inscription
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Delete pending inscriptions older than X days (default: 30)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete pending inscriptions older than this many days (default: 30)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Find old pending inscriptions
        old_inscriptions = Inscription.objects.filter(
            status='PENDING',
            created_at__lt=cutoff_date
        ).select_related('student', 'filiere')
        
        count = old_inscriptions.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f'✅ No pending inscriptions older than {days} days found')
            )
            return
        
        # Show what will be deleted
        self.stdout.write(
            self.style.WARNING(f'\n📋 Found {count} pending inscriptions older than {days} days:')
        )
        
        for inscription in old_inscriptions[:10]:  # Show first 10
            age_days = (timezone.now() - inscription.created_at).days
            self.stdout.write(
                f'   • ID {inscription.id}: {inscription.student.username} → '
                f'{inscription.filiere.code} ({age_days} days old)'
            )
        
        if count > 10:
            self.stdout.write(f'   ... and {count - 10} more')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\n🔍 DRY RUN: Would delete {count} inscriptions '
                    f'(run without --dry-run to actually delete)'
                )
            )
        else:
            # Confirm deletion
            self.stdout.write(
                self.style.WARNING(f'\n⚠️  About to delete {count} old inscriptions!')
            )
            confirm = input('Type "yes" to confirm: ')
            
            if confirm.lower() == 'yes':
                deleted = old_inscriptions.delete()[0]
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Deleted {deleted} old pending inscriptions')
                )
            else:
                self.stdout.write(self.style.WARNING('❌ Cancelled'))