from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q

from .models import Departement, Filiere, Module, Inscription
from .serializers import (
    DepartementSerializer, 
    FiliereSerializer, 
    FiliereListSerializer,
    ModuleSerializer, 
    InscriptionSerializer,
    InscriptionCreateSerializer,
    InscriptionValidateSerializer
)

# ============================================
# CUSTOM PERMISSIONS
# ============================================
class IsAdminOrReadOnly(IsAuthenticated):
    """ADMIN can edit, others can only read"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        return request.user.role in ['ADMIN', 'DIRECTION']


class IsAdminOnly(IsAuthenticated):
    """Only ADMIN can access"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role == 'ADMIN'


# ============================================
# DEPARTEMENT VIEWSET
# ============================================
class DepartementViewSet(viewsets.ModelViewSet):
    queryset = Departement.objects.all()
    serializer_class = DepartementSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # ADMIN sees only their department
        if self.request.user.role == 'ADMIN':
            return queryset.filter(manager=self.request.user)
        
        # DIRECTION sees all
        return queryset


# ============================================
# FILIERE VIEWSET
# ============================================
class FiliereViewSet(viewsets.ModelViewSet):
    queryset = Filiere.objects.select_related('departement').all()
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FiliereListSerializer
        return FiliereSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by department if ADMIN
        if self.request.user.role == 'ADMIN':
            managed_depts = self.request.user.managed_departments.all()
            queryset = queryset.filter(departement__in=managed_depts)
        
        # Filter by query params
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
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # ENSEIGNANT sees only their modules
        if self.request.user.role == 'ENSEIGNANT':
            return queryset.filter(enseignant=self.request.user)
        
        # ADMIN sees modules in their department
        if self.request.user.role == 'ADMIN':
            managed_depts = self.request.user.managed_departments.all()
            queryset = queryset.filter(filiere__departement__in=managed_depts)
        
        # Filter by query params
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
# INSCRIPTION VIEWSET (GOVERNANCE CRITICAL)
# ============================================
class InscriptionViewSet(viewsets.ModelViewSet):
    queryset = Inscription.objects.select_related(
        'student', 'filiere', 'validated_by'
    ).all()
    permission_classes = [IsAuthenticated]
    
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