from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartementViewSet,
    FiliereViewSet,
    ModuleViewSet,
    InscriptionViewSet
)

router = DefaultRouter()
router.register(r'departements', DepartementViewSet, basename='departement')
router.register(r'filieres', FiliereViewSet, basename='filiere')
router.register(r'modules', ModuleViewSet, basename='module')
router.register(r'inscriptions', InscriptionViewSet, basename='inscription')

urlpatterns = [
    path('', include(router.urls)),
]