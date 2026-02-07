from rest_framework import serializers
from .models import Departement, Filiere, Module, Inscription, Note
from django.contrib.auth import get_user_model

User = get_user_model()

# ============================================
# USER SERIALIZER (Light version for nested data)
# ============================================
class UserLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']


# ============================================
# DEPARTEMENT SERIALIZERS
# ============================================
class DepartementSerializer(serializers.ModelSerializer):
    manager_details = UserLightSerializer(source='manager', read_only=True)
    filieres_count = serializers.IntegerField(source='filieres.count', read_only=True)
    
    class Meta:
        model = Departement
        fields = [
            'id', 'name', 'code', 'description', 
            'manager', 'manager_details', 'filieres_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_code(self, value):
        """Ensure department code is uppercase and unique"""
        if value:
            value = value.upper()
            # Check uniqueness (excluding current instance on update)
            qs = Departement.objects.filter(code=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(f"Le code {value} est déjà utilisé.")
        return value
    
    def validate_manager(self, value):
        """Ensure manager has ADMIN role"""
        if value and value.role != 'ADMIN':
            raise serializers.ValidationError(
                "Le chef de département doit avoir le rôle ADMIN."
            )
        return value


# ============================================
# FILIERE SERIALIZERS
# ============================================
class FiliereSerializer(serializers.ModelSerializer):
    departement_details = DepartementSerializer(source='departement', read_only=True)
    modules_count = serializers.IntegerField(source='modules.count', read_only=True)
    inscriptions_count = serializers.IntegerField(source='inscriptions.count', read_only=True)
    
    class Meta:
        model = Filiere
        fields = [
            'id', 'name', 'code', 'departement', 'departement_details',
            'niveau', 'capacity', 'description',
            'modules_count', 'inscriptions_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_capacity(self, value):
        """Ensure capacity is reasonable"""
        if value < 10:
            raise serializers.ValidationError("La capacité minimale est de 10 étudiants.")
        if value > 500:
            raise serializers.ValidationError("La capacité maximale est de 500 étudiants.")
        return value
    
    def validate_code(self, value):
        """Ensure code is uppercase"""
        return value.upper() if value else value


class FiliereListSerializer(serializers.ModelSerializer):
    """Lightweight version for list views"""
    departement_name = serializers.CharField(source='departement.name', read_only=True)
    
    class Meta:
        model = Filiere
        fields = ['id', 'name', 'code', 'departement_name', 'niveau', 'capacity']


# ============================================
# MODULE SERIALIZERS
# ============================================
class ModuleSerializer(serializers.ModelSerializer):
    filiere_details = FiliereListSerializer(source='filiere', read_only=True)
    enseignant_details = UserLightSerializer(source='enseignant', read_only=True)
    total_heures = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = [
            'id', 'name', 'code', 'filiere', 'filiere_details',
            'enseignant', 'enseignant_details',
            'semestre', 'coefficient',
            'heures_cm', 'heures_td', 'heures_tp', 'total_heures',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_heures(self, obj):
        return obj.heures_cm + obj.heures_td + obj.heures_tp
    
    def validate_enseignant(self, value):
        """Ensure enseignant has ENSEIGNANT role"""
        if value and value.role != 'ENSEIGNANT':
            raise serializers.ValidationError(
                "L'enseignant doit avoir le rôle ENSEIGNANT."
            )
        return value
    
    def validate(self, data):
        """Validate that total hours is reasonable"""
        heures_cm = data.get('heures_cm', 0)
        heures_td = data.get('heures_td', 0)
        heures_tp = data.get('heures_tp', 0)
        total = heures_cm + heures_td + heures_tp
        
        if total > 100:
            raise serializers.ValidationError(
                "Le total des heures ne peut pas dépasser 100h par semestre."
            )
        if total < 10:
            raise serializers.ValidationError(
                "Le total des heures doit être d'au moins 10h."
            )
        
        return data


# ============================================
# INSCRIPTION SERIALIZERS (GOVERNANCE)
# ============================================
class InscriptionSerializer(serializers.ModelSerializer):
    # 1. Existing Nested Data (Keep these for Student/Teacher Dashboards)
    student_details = UserLightSerializer(source='student', read_only=True)
    filiere_details = FiliereListSerializer(source='filiere', read_only=True)
    validated_by_details = UserLightSerializer(source='validated_by', read_only=True)
    
    # 2. NEW FLATTENED DATA (Required for Director & Admin Tables)
    student_name = serializers.SerializerMethodField()
    filiere_name = serializers.ReadOnlyField(source='filiere.name')
    departement_name = serializers.ReadOnlyField(source='filiere.departement.name')
    validator_name = serializers.SerializerMethodField()

    class Meta:
        model = Inscription
        fields = [
            'id', 
            'student', 'student_details', 'student_name', # <--- Added student_name
            'filiere', 'filiere_details', 'filiere_name', 'departement_name', # <--- Added names
            'academic_year', 'status',
            'validated_by', 'validated_by_details', 'validator_name', # <--- Added validator_name
            'validation_date', 'rejection_reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'validated_by', 'validation_date']

    # 3. Helper Methods to Format Names safely
    def get_student_name(self, obj):
        if obj.student:
            return f"{obj.student.last_name.upper()} {obj.student.first_name}"
        return "Inconnu"

    def get_validator_name(self, obj):
        if obj.validated_by:
            return f"{obj.validated_by.last_name.upper()} {obj.validated_by.first_name}"
        return "-"
    
class InscriptionCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for students creating inscriptions"""
    class Meta:
        model = Inscription
        fields = ['filiere', 'academic_year']
    
    def validate_filiere(self, value):
        """Validate that the filiere exists and is accepting inscriptions"""
        if not value:
            raise serializers.ValidationError("La filière est obligatoire.")
        
        # Check if filiere is at capacity
        current_inscriptions = Inscription.objects.filter(
            filiere=value,
            status__in=['PENDING', 'VALIDATED']
        ).count()
        
        if current_inscriptions >= value.capacity:
            raise serializers.ValidationError(
                f"La filière {value.name} a atteint sa capacité maximale ({value.capacity} places)."
            )
        
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context manquant.")
        
        student = request.user
        filiere = data.get('filiere')
        academic_year = data.get('academic_year')
        
        # 1. Check if student already has an inscription for this filiere this year
        existing_inscription = Inscription.objects.filter(
            student=student,
            filiere=filiere,
            academic_year=academic_year
        ).exists()
        
        if existing_inscription:
            raise serializers.ValidationError({
                'filiere': f"Vous avez déjà une inscription pour {filiere.name} en {academic_year}."
            })
        
        # 2. Check if student has any PENDING inscription (limit to 1 pending at a time)
        pending_count = Inscription.objects.filter(
            student=student,
            status='PENDING'
        ).count()
        
        if pending_count >= 3:  # Allow max 3 pending applications
            raise serializers.ValidationError(
                "Vous avez déjà 3 candidatures en attente. Veuillez attendre leur validation."
            )
        
        # 3. Validate academic year format (should be like "2024-2025")
        if not academic_year or len(academic_year.split('-')) != 2:
            raise serializers.ValidationError({
                'academic_year': "Le format de l'année académique doit être YYYY-YYYY (ex: 2024-2025)."
            })
        
        try:
            year_start, year_end = academic_year.split('-')
            if int(year_end) - int(year_start) != 1:
                raise ValueError
        except (ValueError, TypeError):
            raise serializers.ValidationError({
                'academic_year': "Année académique invalide. Format attendu: 2024-2025"
            })
        
        return data
    
    def create(self, validated_data):
        # Auto-assign student from request context
        validated_data['student'] = self.context['request'].user
        validated_data['status'] = 'PENDING'
        return super().create(validated_data)


class InscriptionValidateSerializer(serializers.Serializer):
    """Serializer for ADMIN to validate/reject inscriptions"""
    status = serializers.ChoiceField(choices=['VALIDATED', 'REJECTED'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        if data['status'] == 'REJECTED' and not data.get('rejection_reason'):
            raise serializers.ValidationError({
                'rejection_reason': 'Un motif de rejet est requis.'
            })
        return data
    


# ============================================
# NOTE SERIALIZERS
# ============================================
class NoteSerializer(serializers.ModelSerializer):
    student_details = UserLightSerializer(source='student', read_only=True)
    module_details = ModuleSerializer(source='module', read_only=True)
    saisie_par_details = UserLightSerializer(source='saisie_par', read_only=True)
    
    class Meta:
        model = Note
        fields = [
            'id', 'student', 'student_details',
            'module', 'module_details',
            'academic_year',
            'note_controle', 'note_examen', 'note_finale',
            'saisie_par', 'saisie_par_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['note_finale', 'created_at', 'updated_at', 'saisie_par']


class NoteCreateUpdateSerializer(serializers.ModelSerializer):
    """For teachers to enter/update grades"""
    
    class Meta:
        model = Note
        fields = ['student', 'module', 'academic_year', 'note_controle', 'note_examen']
    
    def validate_note_controle(self, value):
        if value is not None and (value < 0 or value > 20):
            raise serializers.ValidationError("La note de contrôle doit être entre 0 et 20")
        return value
    
    def validate_note_examen(self, value):
        if value is not None and (value < 0 or value > 20):
            raise serializers.ValidationError("La note d'examen doit être entre 0 et 20")
        return value
    
    def validate(self, data):
        """Ensure teacher can only grade students in their modules"""
        request = self.context.get('request')
        module = data.get('module')
        
        # Check if teacher is assigned to this module
        if request and request.user.role == 'ENSEIGNANT':
            if module.enseignant != request.user:
                raise serializers.ValidationError(
                    "Vous ne pouvez saisir des notes que pour vos propres modules"
                )
        
        return data


class StudentGradeSerializer(serializers.ModelSerializer):
    """Lightweight serializer for student grade overview"""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_cne = serializers.CharField(source='student.cne', read_only=True)
    module_name = serializers.CharField(source='module.name', read_only=True)
    module_code = serializers.CharField(source='module.code', read_only=True)
    
    class Meta:
        model = Note
        fields = [
            'id', 'student_name', 'student_cne', 
            'module_name', 'module_code',
            'note_controle', 'note_examen', 'note_finale'
        ]