"""
Management command to populate database for ACADEMIYATI case study
Atelier 1: 20 Admins, 60 Profs, 4 Départements (Info, Finance, Marketing, Gestion)
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Departement, Filiere, Module, Inscription
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database for ACADEMIYATI scenario'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('⚠️  DÉBUT DU NETTOYAGE ET DE LA POPULATION ACADEMIYATI...'))

        # ============================================
        # 0. NETTOYAGE (DELETE OLD DATA)
        # ============================================
        self.stdout.write('🗑️ Suppression des anciennes données...')
        # La suppression des utilisateurs supprime en cascade les inscriptions, profils, etc.
        # On garde les superusers si on veut, mais ici on reset tout pour être propre.
        User.objects.exclude(is_superuser=True).delete()
        Departement.objects.all().delete()
        Filiere.objects.all().delete()
        Module.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('✅ Base de données nettoyée.'))

        # ============================================
        # 1. CRÉATION DES DÉPARTEMENTS (Les Silos)
        # ============================================
        dept_names = ['Informatique', 'Finance', 'Marketing', 'Gestion']
        depts = {}
        
        # On crée d'abord les départements sans chef pour l'instant
        for name in dept_names:
            code = name[:4].upper()
            d = Departement.objects.create(
                name=name,
                code=code,
                description=f"Département de {name} - ACADEMIYATI"
            )
            depts[name] = d
        
        self.stdout.write(self.style.SUCCESS('✅ 4 Départements créés (Silos).'))

        # ============================================
        # 2. CRÉATION DU PERSONNEL (20 Admin + 60 Profs)
        # ============================================
        self.stdout.write('👥 Création du personnel...')

        # --- A. DIRECTION (1 Directeur) ---
        directeur = User.objects.create_user(
            username='directeur',
            email='directeur@academiyati.ma',
            password='password123',
            first_name='Directeur',
            last_name='Général',
            role='DIRECTION',
            matricule='DIR001'
        )

        # --- B. ADMINISTRATEURS (Total 20 : 1 Directeur + 19 Admins/Staff) ---
        admins = []
        # On crée 4 chefs de départements (qui sont aussi des admins dans ce scénario)
        for i, name in enumerate(dept_names):
            chef = User.objects.create_user(
                username=f'chef_{name.lower()}',
                email=f'chef.{name.lower()}@academiyati.ma',
                password='password123',
                first_name=f'Chef',
                last_name=name,
                role='ADMIN',
                matricule=f'ADM{i+1:03d}'
            )
            admins.append(chef)
            # Assigner le chef au département
            dept = depts[name]
            dept.manager = chef
            dept.save()

        # On crée 15 autres administrateurs (secrétaires, scolarité, etc.) pour atteindre 20 total
        for i in range(15):
            admin = User.objects.create_user(
                username=f'admin_{i+1}',
                email=f'staff.{i+1}@academiyati.ma',
                password='password123',
                first_name=f'Staff',
                last_name=f'Administratif {i+1}',
                role='ADMIN',
                matricule=f'ADM_S{i+1:03d}'
            )

        self.stdout.write(self.style.SUCCESS('✅ 20 Administrateurs créés (dont 1 Directeur et 4 Chefs).'))

        # --- C. PROFESSEURS (Total 60) ---
        # 15 Profs par département pour équilibrer
        profs = []
        count_prof = 0
        for dept_name in dept_names:
            for i in range(15): # 15 * 4 = 60
                count_prof += 1
                prof = User.objects.create_user(
                    username=f'prof_{dept_name.lower()}_{i+1}',
                    email=f'prof.{dept_name.lower()}.{i+1}@academiyati.ma',
                    password='password123',
                    first_name=f'Prof',
                    last_name=f'{dept_name} {i+1}',
                    role='ENSEIGNANT',
                    matricule=f'ENS{count_prof:03d}'
                )
                profs.append(prof)
        
        self.stdout.write(self.style.SUCCESS(f'✅ {count_prof} Professeurs créés.'))

        # ============================================
        # 3. STRUCTURE PÉDAGOGIQUE & ÉTUDIANTS
        # ============================================
        
        # Filières
        filiere_info = Filiere.objects.create(name="Génie Logiciel", code="GL", departement=depts['Informatique'], capacity=100)
        filiere_fin = Filiere.objects.create(name="Audit & Contrôle", code="AC", departement=depts['Finance'], capacity=80)
        filiere_mark = Filiere.objects.create(name="Marketing Digital", code="MD", departement=depts['Marketing'], capacity=80)
        filiere_gest = Filiere.objects.create(name="Gestion Entreprises", code="GE", departement=depts['Gestion'], capacity=120)
        
        filieres = [filiere_info, filiere_fin, filiere_mark, filiere_gest]

        # Création de Modules (Pour avoir des "Cours Actifs")
        # On assigne des profs aléatoires aux modules
        modules_list = [
            ('Base de données', filiere_info), ('Algorithmique', filiere_info), ('Python', filiere_info),
            ('Comptabilité', filiere_fin), ('Finance Marché', filiere_fin),
            ('SEO', filiere_mark), ('Comportement Consommateur', filiere_mark),
            ('Management', filiere_gest), ('GRH', filiere_gest)
        ]

        for mod_name, fil in modules_list:
            # Trouver un prof du département concerné par la filière n'est pas strict ici, 
            # on prend un prof au hasard pour simplifier ou les premiers de la liste
            Module.objects.create(
                name=mod_name,
                code=mod_name[:3].upper(),
                filiere=fil,
                semestre=1,
                enseignant=profs[random.randint(0, 59)] # Assign random prof
            )

        # --- D. ÉTUDIANTS (Simulation de masse) ---
        # On va créer 200 étudiants pour avoir des stats
        self.stdout.write('🎓 Création des étudiants et inscriptions...')
        
        statuses = ['VALIDATED', 'PENDING', 'REJECTED']
        
        for i in range(200):
            student = User.objects.create_user(
                username=f'etudiant_{i+1}',
                email=f'etu.{i+1}@academiyati.ma',
                password='password123',
                first_name=f'Etudiant',
                last_name=f'{i+1}',
                role='ETUDIANT',
                cne=f'CNE{2025000+i}'
            )
            
            # Inscription aléatoire
            fil = random.choice(filieres)
            stat = random.choices(statuses, weights=[70, 20, 10], k=1)[0] # 70% validés
            
            Inscription.objects.create(
                student=student,
                filiere=fil,
                academic_year='2024-2025',
                status=stat,
                validation_date=timezone.now() if stat == 'VALIDATED' else None
            )

        self.stdout.write(self.style.SUCCESS('✅ 200 Étudiants inscrits.'))

        # ============================================
        # RÉSUMÉ POUR L'ATELIER
        # ============================================
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('🚀 ACADEMIYATI - SETUP COMPLET'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'🔹 ADMINS   : {User.objects.filter(role="ADMIN").count()} (Dont chefs dépts)')
        self.stdout.write(f'🔹 DIRECTION: {User.objects.filter(role="DIRECTION").count()}')
        self.stdout.write(f'🔹 PROFS    : {User.objects.filter(role="ENSEIGNANT").count()}')
        self.stdout.write(f'🔹 ÉTUDIANTS: {User.objects.filter(role="ETUDIANT").count()}')
        self.stdout.write(self.style.WARNING('\n🔑 IDENTIFIANTS TEST (Mot de passe: password123)'))
        self.stdout.write('   - Directeur: directeur')
        self.stdout.write('   - Chef Info: chef_informatique')
        self.stdout.write('   - Prof Info: prof_informatique_1')
        self.stdout.write('   - Etudiant : etudiant_1')