from rest_framework import serializers
from .models import Departement, Filiere, Module, Inscription
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


# ============================================
# INSCRIPTION SERIALIZERS (GOVERNANCE)
# ============================================
class InscriptionSerializer(serializers.ModelSerializer):
    student_details = UserLightSerializer(source='student', read_only=True)
    filiere_details = FiliereListSerializer(source='filiere', read_only=True)
    validated_by_details = UserLightSerializer(source='validated_by', read_only=True)
    
    class Meta:
        model = Inscription
        fields = [
            'id', 'student', 'student_details',
            'filiere', 'filiere_details',
            'academic_year', 'status',
            'validated_by', 'validated_by_details',
            'validation_date', 'rejection_reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'validated_by', 'validation_date']


class InscriptionCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for students creating inscriptions"""
    class Meta:
        model = Inscription
        fields = ['filiere', 'academic_year']
    
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