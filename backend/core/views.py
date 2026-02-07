from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from django.utils import timezone
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes, action, authentication_classes
from django.db.models import Count
from users.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication  # <--- Critical for 401 fix
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.contrib.auth import get_user_model
from django.db.models import Sum # <--- N'oublie pas cet import en haut !
from django.db.models import Avg, F


from .models import Departement, Filiere, Module, Inscription, Note
from .serializers import (
    DepartementSerializer, 
    FiliereSerializer, 
    FiliereListSerializer,
    ModuleSerializer, 
    InscriptionSerializer,
    InscriptionCreateSerializer,
    InscriptionValidateSerializer,
     NoteSerializer,
    NoteCreateUpdateSerializer,
    StudentGradeSerializer,
)

User = get_user_model()
# ============================================
# CUSTOM PERMISSIONS (FIXED!)
# ============================================
class IsAdminOrReadOnly:
    """
    FIXED: Allow public read access, ADMIN can edit
    Anyone can GET, only ADMIN can POST/PUT/DELETE
    """
    def has_permission(self, request, view):
        # Allow all read operations (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True
        
        # For write operations, must be authenticated and be ADMIN
        return request.user and request.user.is_authenticated and request.user.role in ['ADMIN', 'DIRECTION']


class IsAdminOnly:
    """Only authenticated ADMIN can access"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'


# ============================================
# DEPARTEMENT VIEWSET
# ============================================
class DepartementViewSet(viewsets.ModelViewSet):
    queryset = Departement.objects.all()
    serializer_class = DepartementSerializer
    permission_classes = [IsAdminOrReadOnly]  # Public read, ADMIN write
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # ADMIN sees only their department (when authenticated)
        if self.request.user.is_authenticated and self.request.user.role == 'ADMIN':
            return queryset.filter(manager=self.request.user)
        
        # Everyone else (including anonymous) sees all
        return queryset


# ============================================
# FILIERE VIEWSET
# ============================================
class FiliereViewSet(viewsets.ModelViewSet):
    queryset = Filiere.objects.select_related('departement').all()
    permission_classes = [IsAdminOrReadOnly]  # Public read, ADMIN write
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FiliereListSerializer
        return FiliereSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by department if ADMIN (when authenticated)
        if self.request.user.is_authenticated and self.request.user.role == 'ADMIN':
            managed_depts = self.request.user.managed_departments.all()
            queryset = queryset.filter(departement__in=managed_depts)
        
        # Filter by query params (available to everyone)
        dept_id = self.request.query_params.get('departement')
        if dept_id:
            queryset = queryset.filter(departement_id=dept_id)
        
        niveau = self.request.query_params.get('niveau')
        if niveau:
            queryset = queryset.filter(niveau=niveau)
        
        return queryset


# ============================================
# MODULE VIEWSET
# ============================================
class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.select_related('filiere', 'enseignant').all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAdminOrReadOnly]  # Public read, ADMIN write
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Only filter if user is authenticated
        if not self.request.user.is_authenticated:
            return queryset
        
        # ENSEIGNANT sees only their modules
        if self.request.user.role == 'ENSEIGNANT':
            return queryset.filter(enseignant=self.request.user)
        
        # ADMIN sees modules in their department
        if self.request.user.role == 'ADMIN':
            managed_depts = self.request.user.managed_departments.all()
            queryset = queryset.filter(filiere__departement__in=managed_depts)
        
        # Filter by query params (available to everyone)
        filiere_id = self.request.query_params.get('filiere')
        if filiere_id:
            queryset = queryset.filter(filiere_id=filiere_id)
        
        semestre = self.request.query_params.get('semestre')
        if semestre:
            queryset = queryset.filter(semestre=semestre)
        
        return queryset
    
    def perform_create(self, serializer):
        # Only ADMIN can create modules
        if self.request.user.role != 'ADMIN':
            return Response(
                {'error': 'Seuls les administrateurs peuvent créer des modules.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()


# ============================================
# INSCRIPTION VIEWSET (REQUIRES AUTH)
# ============================================
class InscriptionViewSet(viewsets.ModelViewSet):
    queryset = Inscription.objects.select_related(
        'student', 'filiere', 'validated_by'
    ).all()
    permission_classes = [IsAuthenticated]  # All inscription operations require auth
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InscriptionCreateSerializer
        if self.action == 'validate':
            return InscriptionValidateSerializer
        return InscriptionSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # ETUDIANT sees only their inscriptions
        if self.request.user.role == 'ETUDIANT':
            return queryset.filter(student=self.request.user)
        
        # ADMIN sees inscriptions in their department
        if self.request.user.role == 'ADMIN':
            managed_depts = self.request.user.managed_departments.all()
            queryset = queryset.filter(filiere__departement__in=managed_depts)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by academic year
        year = self.request.query_params.get('academic_year')
        if year:
            queryset = queryset.filter(academic_year=year)
        
        return queryset
    
    def perform_create(self, serializer):
        # Only ETUDIANT can create inscriptions
        if self.request.user.role != 'ETUDIANT':
            return Response(
                {'error': 'Seuls les étudiants peuvent créer des inscriptions.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminOnly])
    def validate(self, request, pk=None):
        """
        ADMIN endpoint to validate/reject inscriptions
        POST /api/inscriptions/{id}/validate/
        Body: {"status": "VALIDATED"} or {"status": "REJECTED", "rejection_reason": "..."}
        """
        inscription = self.get_object()
        
        # Check if already processed
        if inscription.status != 'PENDING':
            return Response(
                {'error': f'Cette inscription est déjà {inscription.get_status_display()}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = InscriptionValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Update inscription
        inscription.status = serializer.validated_data['status']
        inscription.validated_by = request.user
        inscription.validation_date = timezone.now()
        
        if serializer.validated_data['status'] == 'REJECTED':
            inscription.rejection_reason = serializer.validated_data.get('rejection_reason', '')
        
        inscription.save()
        
        return Response(
            InscriptionSerializer(inscription).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def my_inscriptions(self, request):
        """
        ETUDIANT endpoint to get their own inscriptions
        GET /api/inscriptions/my_inscriptions/
        """
        if request.user.role != 'ETUDIANT':
            return Response(
                {'error': 'Endpoint réservé aux étudiants.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        inscriptions = self.queryset.filter(student=request.user)
        serializer = InscriptionSerializer(inscriptions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminOnly])
    def pending(self, request):
        """
        ADMIN endpoint to get all pending inscriptions in their department
        GET /api/inscriptions/pending/
        """
        managed_depts = request.user.managed_departments.all()
        pending = self.queryset.filter(
            status='PENDING',
            filiere__departement__in=managed_depts
        )
        serializer = InscriptionSerializer(pending, many=True)
        return Response(serializer.data)
    


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated]) # Ou AllowAny pour tester
def dashboard_statistics(request):
    
    # 1. CHIFFRES DE BASE
    total_students = User.objects.filter(role='ETUDIANT').count()
    total_profs = User.objects.filter(role='ENSEIGNANT').count()
    pending_count = Inscription.objects.filter(status='PENDING').count()
    
    # 2. CALCUL DU TAUX DE REMPLISSAGE (Occupancy)
    # Somme de la capacité de toutes les filières
    total_capacity = Filiere.objects.aggregate(Sum('capacity'))['capacity__sum'] or 1
    # Nombre d'inscriptions validées (étudiants réellement assis en classe)
    active_students = Inscription.objects.filter(status='VALIDATED').count()
    
    occupancy_rate = round((active_students / total_capacity) * 100, 1) if total_capacity > 0 else 0
    
    # 3. CALCUL DU TAUX D'ADMISSION (Selectivity)
    total_applications = Inscription.objects.count() or 1
    admission_rate = round((active_students / total_applications) * 100, 1)

    # 4. CONSTRUCTION DE LA RÉPONSE
    kpi_data = [
        # Carte 1 : Volume Étudiants
        {"label": "Total Étudiants", "value": total_students, "icon": "Users", "color": "blue"},
        
        # Carte 2 : Bottleneck (Urgence)
        {"label": "Dossiers en Attente", "value": pending_count, "icon": "Clock", "color": "amber"},
        
        # Carte 3 : Performance (Nouveau !)
        {"label": "Taux de Remplissage", "value": f"{occupancy_rate}%", "icon": "Maximize", "color": "emerald"},
        
        # Carte 4 : Sélectivité (Nouveau !)
        {"label": "Taux d'Admission", "value": f"{admission_rate}%", "icon": "Filter", "color": "purple"},
    ]

    # ... (Garde le reste du code pour enrollment_trends et department_dist) ...
    
    # Reste du code inchangé pour les graphiques
    trends_query = Inscription.objects.filter(status='VALIDATED').annotate(month=TruncMonth('validation_date')).values('month').annotate(count=Count('id')).order_by('month')
    enrollment_trends = [{"name": item['month'].strftime('%b'), "count": item['count']} for item in trends_query if item['month']]
    
    dept_query = Inscription.objects.filter(status='VALIDATED').values('filiere__departement__name').annotate(value=Count('id'))
    department_dist = [{"name": item['filiere__departement__name'], "value": item['value']} for item in dept_query]

    return Response({
        "kpi": kpi_data,
        "enrollment_trends": enrollment_trends,
        "department_dist": department_dist
    })



# ============================================
# CUSTOM PERMISSION FOR TEACHERS
# ============================================
class IsTeacherOnly:
    """Only authenticated ENSEIGNANT can access"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ENSEIGNANT'


# ============================================
# NOTE VIEWSET (For Teachers)
# ============================================
class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.select_related('student', 'module', 'saisie_par').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return NoteCreateUpdateSerializer
        if self.action == 'students_grades':
            return StudentGradeSerializer
        return NoteSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # ENSEIGNANT sees only grades for their modules
        if self.request.user.role == 'ENSEIGNANT':
            return queryset.filter(module__enseignant=self.request.user)
        
        # ETUDIANT sees only their own grades
        if self.request.user.role == 'ETUDIANT':
            return queryset.filter(student=self.request.user)
        
        # ADMIN/DIRECTION see all
        return queryset
    
    def perform_create(self, serializer):
        # Auto-assign saisie_par to current teacher
        if self.request.user.role == 'ENSEIGNANT':
            serializer.save(saisie_par=self.request.user)
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        # Update saisie_par on modification
        if self.request.user.role == 'ENSEIGNANT':
            serializer.save(saisie_par=self.request.user)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'], permission_classes=[IsTeacherOnly])
    def my_modules(self, request):
        """
        TEACHER endpoint to get their assigned modules with student count
        GET /api/notes/my_modules/
        """
        modules = Module.objects.filter(enseignant=request.user).annotate(
            student_count=Count('filiere__inscriptions', filter=Q(filiere__inscriptions__status='VALIDATED'))
        )
        
        data = []
        for module in modules:
            data.append({
                'id': module.id,
                'name': module.name,
                'code': module.code,
                'filiere': module.filiere.name,
                'semestre': module.semestre,
                'student_count': module.student_count,
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsTeacherOnly])
    def students_by_module(self, request):
        """
        TEACHER endpoint to get list of students for a specific module
        GET /api/notes/students_by_module/?module_id=1&academic_year=2024-2025
        """
        module_id = request.query_params.get('module_id')
        academic_year = request.query_params.get('academic_year', '2024-2025')
        
        if not module_id:
            return Response({'error': 'module_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            module = Module.objects.get(id=module_id, enseignant=request.user)
        except Module.DoesNotExist:
            return Response({'error': 'Module not found or not assigned to you'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get validated students enrolled in this module's filiere
        students = User.objects.filter(
            role='ETUDIANT',
            inscriptions__filiere=module.filiere,
            inscriptions__status='VALIDATED',
            inscriptions__academic_year=academic_year
        ).distinct()
        
        # Get existing grades for these students
        data = []
        for student in students:
            try:
                note = Note.objects.get(
                    student=student,
                    module=module,
                    academic_year=academic_year
                )
                data.append({
                    'student_id': student.id,
                    'student_name': f"{student.first_name} {student.last_name}",
                    'cne': student.cne,
                    'note_id': note.id,
                    'note_controle': note.note_controle,
                    'note_examen': note.note_examen,
                    'note_finale': note.note_finale,
                })
            except Note.DoesNotExist:
                # Student doesn't have grade yet
                data.append({
                    'student_id': student.id,
                    'student_name': f"{student.first_name} {student.last_name}",
                    'cne': student.cne,
                    'note_id': None,
                    'note_controle': None,
                    'note_examen': None,
                    'note_finale': None,
                })
        
        return Response({
            'module': {
                'id': module.id,
                'name': module.name,
                'code': module.code,
            },
            'academic_year': academic_year,
            'students': data
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsTeacherOnly])
    def bulk_update_grades(self, request):
        """
        TEACHER endpoint to update multiple grades at once
        POST /api/notes/bulk_update_grades/
        Body: {
            "module_id": 1,
            "academic_year": "2024-2025",
            "grades": [
                {"student_id": 1, "note_controle": 15, "note_examen": 16},
                {"student_id": 2, "note_controle": 12, "note_examen": 14}
            ]
        }
        """
        module_id = request.data.get('module_id')
        academic_year = request.data.get('academic_year')
        grades = request.data.get('grades', [])
        
        if not module_id or not academic_year:
            return Response(
                {'error': 'module_id and academic_year are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            module = Module.objects.get(id=module_id, enseignant=request.user)
        except Module.DoesNotExist:
            return Response(
                {'error': 'Module not found or not assigned to you'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        updated_count = 0
        for grade_data in grades:
            student_id = grade_data.get('student_id')
            note_controle = grade_data.get('note_controle')
            note_examen = grade_data.get('note_examen')
            
            try:
                student = User.objects.get(id=student_id, role='ETUDIANT')
                
                # Create or update note
                note, created = Note.objects.update_or_create(
                    student=student,
                    module=module,
                    academic_year=academic_year,
                    defaults={
                        'note_controle': note_controle,
                        'note_examen': note_examen,
                        'saisie_par': request.user
                    }
                )
                updated_count += 1
            except User.DoesNotExist:
                continue
        
        return Response({
            'success': True,
            'updated_count': updated_count,
            'message': f'{updated_count} notes mises à jour avec succès'
        })
    

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def academic_performance(request):
    # 1. Moyenne Générale de l'École
    global_avg = Note.objects.aggregate(Avg('note_finale'))['note_finale__avg'] or 0
    
    # 2. Taux de Réussite (Notes >= 10)
    total_notes = Note.objects.count() or 1
    passing_notes = Note.objects.filter(note_finale__gte=10).count()
    success_rate = round((passing_notes / total_notes) * 100, 1)

    # 3. Performance par Filière (Pour le graphique)
    # On groupe par Filière et on fait la moyenne des notes finales
    perf_by_filiere = (
        Note.objects
        .values('module__filiere__name')
        .annotate(moyenne=Avg('note_finale'))
        .order_by('-moyenne')
    )
    
    chart_data = [
        {"name": item['module__filiere__name'], "value": round(item['moyenne'], 2)} 
        for item in perf_by_filiere if item['module__filiere__name']
    ]

    # 4. Top 5 Étudiants (Majors de Promo)
    # On calcule la moyenne de chaque étudiant
    top_students = (
        Note.objects
        .values('student__first_name', 'student__last_name', 'module__filiere__name')
        .annotate(general_avg=Avg('note_finale'))
        .order_by('-general_avg')[:5] # Les 5 meilleurs
    )

    top_list = [
        {
            "name": f"{s['student__last_name'].upper()} {s['student__first_name']}",
            "filiere": s['module__filiere__name'],
            "average": round(s['general_avg'], 2)
        }
        for s in top_students
    ]

    return Response({
        "global_average": round(global_avg, 2),
        "success_rate": success_rate,
        "chart_data": chart_data,
        "top_students": top_list
    })