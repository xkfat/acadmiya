"""
Management command to populate database with sample data
Usage: python manage.py populate_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Departement, Filiere, Module, Inscription
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with sample academic data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🚀 Starting data population...'))
        
        # ============================================
        # 1. CREATE USERS
        # ============================================
        self.stdout.write('📝 Creating users...')
        
        # Admin/Chef de département
        admin_info, _ = User.objects.get_or_create(
            username='chef_info',
            defaults={
                'email': 'chef.info@academiya.ma',
                'first_name': 'Mohammed',
                'last_name': 'Alami',
                'role': 'ADMIN',
                'matricule': 'ADM001'
            }
        )
        admin_info.set_password('admin123')
        admin_info.save()
        
        admin_gc, _ = User.objects.get_or_create(
            username='chef_gc',
            defaults={
                'email': 'chef.gc@academiya.ma',
                'first_name': 'Fatima',
                'last_name': 'Benali',
                'role': 'ADMIN',
                'matricule': 'ADM002'
            }
        )
        admin_gc.set_password('admin123')
        admin_gc.save()
        
        # Direction
        direction, _ = User.objects.get_or_create(
            username='directeur',
            defaults={
                'email': 'direction@academiya.ma',
                'first_name': 'Ahmed',
                'last_name': 'Tazi',
                'role': 'DIRECTION',
                'matricule': 'DIR001'
            }
        )
        direction.set_password('direction123')
        direction.save()
        
        # Enseignants
        prof1, _ = User.objects.get_or_create(
            username='prof_benkirane',
            defaults={
                'email': 'benkirane@academiya.ma',
                'first_name': 'Youssef',
                'last_name': 'Benkirane',
                'role': 'ENSEIGNANT',
                'matricule': 'ENS001'
            }
        )
        prof1.set_password('prof123')
        prof1.save()
        
        prof2, _ = User.objects.get_or_create(
            username='prof_idrissi',
            defaults={
                'email': 'idrissi@academiya.ma',
                'first_name': 'Samira',
                'last_name': 'Idrissi',
                'role': 'ENSEIGNANT',
                'matricule': 'ENS002'
            }
        )
        prof2.set_password('prof123')
        prof2.save()
        
        prof3, _ = User.objects.get_or_create(
            username='prof_mansouri',
            defaults={
                'email': 'mansouri@academiya.ma',
                'first_name': 'Karim',
                'last_name': 'Mansouri',
                'role': 'ENSEIGNANT',
                'matricule': 'ENS003'
            }
        )
        prof3.set_password('prof123')
        prof3.save()
        
        # Étudiants
        students = []
        student_data = [
            ('etudiant1', 'Amine', 'Chakir', 'CNE123456'),
            ('etudiant2', 'Salma', 'Benjelloun', 'CNE123457'),
            ('etudiant3', 'Omar', 'Senhaji', 'CNE123458'),
            ('etudiant4', 'Lina', 'Filali', 'CNE123459'),
            ('etudiant5', 'Hassan', 'Ouazzani', 'CNE123460'),
        ]
        
        for username, first, last, cne in student_data:
            student, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@etu.academiya.ma',
                    'first_name': first,
                    'last_name': last,
                    'role': 'ETUDIANT',
                    'cne': cne
                }
            )
            student.set_password('etudiant123')
            student.save()
            students.append(student)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(students) + 5} users'))
        
        # ============================================
        # 2. CREATE DEPARTMENTS
        # ============================================
        self.stdout.write('🏛️ Creating departments...')
        
        dept_info, _ = Departement.objects.get_or_create(
            code='INFO',
            defaults={
                'name': 'Informatique',
                'description': 'Département des Sciences Informatiques',
                'manager': admin_info
            }
        )
        
        dept_gc, _ = Departement.objects.get_or_create(
            code='GC',
            defaults={
                'name': 'Génie Civil',
                'description': 'Département de Génie Civil et Construction',
                'manager': admin_gc
            }
        )
        
        self.stdout.write(self.style.SUCCESS('✅ Created 2 departments'))
        
        # ============================================
        # 3. CREATE FILIERES
        # ============================================
        self.stdout.write('📚 Creating filieres...')
        
        # Informatique filieres
        gi, _ = Filiere.objects.get_or_create(
            code='GI',
            departement=dept_info,
            defaults={
                'name': 'Génie Informatique',
                'niveau': 'LICENSE',
                'capacity': 40,
                'description': 'Formation en développement logiciel et systèmes'
            }
        )
        
        rt, _ = Filiere.objects.get_or_create(
            code='RT',
            departement=dept_info,
            defaults={
                'name': 'Réseaux et Télécommunications',
                'niveau': 'LICENSE',
                'capacity': 35,
                'description': 'Formation en réseaux, sécurité et télécom'
            }
        )
        
        # Génie Civil filiere
        gc_lic, _ = Filiere.objects.get_or_create(
            code='GC-L',
            departement=dept_gc,
            defaults={
                'name': 'Génie Civil - Licence',
                'niveau': 'LICENSE',
                'capacity': 50,
                'description': 'Formation de base en génie civil'
            }
        )
        
        self.stdout.write(self.style.SUCCESS('✅ Created 3 filieres'))
        
        # ============================================
        # 4. CREATE MODULES
        # ============================================
        self.stdout.write('📖 Creating modules...')
        
        modules_data = [
            # GI Modules
            {
                'code': 'POO',
                'name': 'Programmation Orientée Objet',
                'filiere': gi,
                'enseignant': prof1,
                'semestre': 3,
                'coefficient': 3.0,
                'heures_cm': 30,
                'heures_td': 20,
                'heures_tp': 20
            },
            {
                'code': 'BDD',
                'name': 'Bases de Données',
                'filiere': gi,
                'enseignant': prof2,
                'semestre': 3,
                'coefficient': 3.0,
                'heures_cm': 25,
                'heures_td': 15,
                'heures_tp': 20
            },
            {
                'code': 'WEB',
                'name': 'Développement Web',
                'filiere': gi,
                'enseignant': prof1,
                'semestre': 4,
                'coefficient': 2.5,
                'heures_cm': 20,
                'heures_td': 15,
                'heures_tp': 25
            },
            # RT Modules
            {
                'code': 'RES',
                'name': 'Réseaux Informatiques',
                'filiere': rt,
                'enseignant': prof3,
                'semestre': 3,
                'coefficient': 3.0,
                'heures_cm': 30,
                'heures_td': 20,
                'heures_tp': 20
            },
            {
                'code': 'SEC',
                'name': 'Sécurité des Systèmes',
                'filiere': rt,
                'enseignant': prof3,
                'semestre': 4,
                'coefficient': 2.5,
                'heures_cm': 25,
                'heures_td': 20,
                'heures_tp': 15
            },
            # GC Modules
            {
                'code': 'RDM',
                'name': 'Résistance des Matériaux',
                'filiere': gc_lic,
                'enseignant': prof2,
                'semestre': 3,
                'coefficient': 3.0,
                'heures_cm': 35,
                'heures_td': 25,
                'heures_tp': 10
            },
        ]
        
        for module_data in modules_data:
            Module.objects.get_or_create(
                code=module_data['code'],
                filiere=module_data['filiere'],
                defaults=module_data
            )
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(modules_data)} modules'))
        
        # ============================================
        # 5. CREATE INSCRIPTIONS
        # ============================================
        self.stdout.write('📝 Creating inscriptions...')
        
        current_year = '2024-2025'
        
        inscriptions_data = [
            # Validated inscriptions
            (students[0], gi, 'VALIDATED', admin_info),
            (students[1], gi, 'VALIDATED', admin_info),
            (students[2], rt, 'VALIDATED', admin_info),
            # Pending inscriptions
            (students[3], gi, 'PENDING', None),
            (students[4], gc_lic, 'PENDING', None),
        ]
        
        for student, filiere, status, validator in inscriptions_data:
            inscription, created = Inscription.objects.get_or_create(
                student=student,
                filiere=filiere,
                academic_year=current_year,
                defaults={
                    'status': status,
                    'validated_by': validator,
                    'validation_date': timezone.now() if validator else None
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(inscriptions_data)} inscriptions'))
        
        # ============================================
        # SUMMARY
        # ============================================
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('✨ DATA POPULATION COMPLETE!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.WARNING('\n📋 LOGIN CREDENTIALS:'))
        self.stdout.write('🔹 ADMIN (Info): chef_info / admin123')
        self.stdout.write('🔹 ADMIN (GC): chef_gc / admin123')
        self.stdout.write('🔹 DIRECTION: directeur / direction123')
        self.stdout.write('🔹 ENSEIGNANT: prof_benkirane / prof123')
        self.stdout.write('🔹 ÉTUDIANT: etudiant1 / etudiant123')
        self.stdout.write(self.style.SUCCESS('\n🚀 Ready to test frontend!\n'))