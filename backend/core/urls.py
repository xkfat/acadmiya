from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartementViewSet,
    FiliereViewSet,
    ModuleViewSet,
    InscriptionViewSet,
    dashboard_statistics,
    NoteViewSet,
)

router = DefaultRouter()
router.register(r'departements', DepartementViewSet, basename='departement')
router.register(r'filieres', FiliereViewSet, basename='filiere')
router.register(r'modules', ModuleViewSet, basename='module')
router.register(r'inscriptions', InscriptionViewSet, basename='inscription')
router.register(r'notes', NoteViewSet, basename='note')  # ← Add this

urlpatterns = [
    path('', include(router.urls)),
    path('statistics/dashboard/', dashboard_statistics, name='stats'),

]