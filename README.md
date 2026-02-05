# 🎓 ACADEMIYA-Hub

**Plateforme Web de Gestion Académique Universitaire**

---

## 📋 Table des Matières

1. [Contexte du Projet](#-contexte-du-projet)
2. [Architecture Technique](#️-architecture-technique)
3. [Choix Techniques](#-choix-techniques)
4. [Fonctionnalités Principales](#-fonctionnalités-principales)
5. [Documentation API](#-documentation-api)
6. [Technologies Utilisées](#️-technologies-utilisées)

---

## 🎯 Contexte du Projet

### Problématique

ACADEMIYATI est une institution d'enseignement supérieur confrontée à plusieurs difficultés majeures :

- **Obsolescence technologique** : Logiciel pédagogique de plus de 15 ans
- **Dispersion des données** : Fichiers Excel séparés par département
- **Absence de gouvernance** : Aucune responsabilité claire sur les données
- **Cloisonnement inter-services** : Faible collaboration entre départements
- **Dépendance critique** : Une seule personne maîtrise le système existant

### Solution : ACADEMIYA-Hub

Plateforme web centralisée permettant :

✅ **La gestion pédagogique complète** (inscriptions, notes, modules, filières)  
✅ **La centralisation des données** (référentiel unique dans base de données SQLite)  
✅ **L'aide à la décision** (tableaux de bord et statistiques en temps réel)  
✅ **La collaboration inter-départements** (accès contrôlé et partagé)

---

## 🏗️ Architecture Technique

### Type d'Architecture : **Architecture Client-Serveur REST API**

```
┌─────────────────────────────────────────────────────────────┐
│                     COUCHE PRÉSENTATION                      │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              React.js (Frontend SPA)                   │  │
│  │  • Vite (Build Tool)                                   │  │
│  │  • React Router (Navigation)                           │  │
│  │  • Tailwind CSS (UI Framework)                         │  │
│  │  • Axios (Client HTTP)                                 │  │
│  └───────────────────────────────────────────────────────┘  │
│                            ▼                                  │
│                   Communication HTTP/JSON                     │
│                            ▼                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           API REST (Django REST Framework)             │  │
│  │  • Endpoints CRUD pour toutes les ressources          │  │
│  │  • Authentification JWT (Simple JWT)                  │  │
│  │  • Permissions par rôle                                │  │
│  │  • Serializers pour validation des données            │  │
│  │  • Documentation Swagger (drf-spectacular)            │  │
│  └───────────────────────────────────────────────────────┘  │
│                            ▼                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              COUCHE MÉTIER (Django ORM)                │  │
│  │  • Models : User, Departement, Filiere, Module,       │  │
│  │             Inscription, Note                          │  │
│  │  • Business Logic : Validation candidatures,           │  │
│  │                     Calcul notes, Statistiques         │  │
│  │  • Permissions personnalisées par rôle                 │  │
│  └───────────────────────────────────────────────────────┘  │
│                            ▼                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            COUCHE DONNÉES (SQLite)                     │  │
│  │  • Base de données relationnelle centralisée           │  │
│  │  • Contraintes d'intégrité (clés étrangères, uniques) │  │
│  │  • Migrations versionnées (Django Migrations)          │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Flux d'Authentification JWT

```
┌──────────┐                  ┌──────────┐                 ┌──────────┐
│          │  1. POST /login  │          │  2. Vérifier    │          │
│  Client  │ ─────────────────→   API    │ ─────────────────→    DB    │
│ (React)  │ email + password │ (Django) │  credentials    │ (SQLite) │
│          │←─────────────────│          │←─────────────────│          │
│          │  3. Access Token │          │  4. User data   │          │
└──────────┘                  └──────────┘                 └──────────┘
     │
     │ 5. Stockage token (localStorage)
     ▼
┌──────────┐
│          │  6. Requêtes avec Header:
│  Client  │     Authorization: Bearer <token>
│          │ ─────────────────────────────────→
└──────────┘
```

### Architecture des Rôles et Permissions

```
┌─────────────────────────────────────────────────────────────┐
│                      Modèle de Permissions                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ÉTUDIANT                    ENSEIGNANT                      │
│  ├─ Soumettre candidature    ├─ Voir modules assignés       │
│  ├─ Consulter inscriptions   ├─ Consulter étudiants         │
│  └─ Consulter notes          └─ Saisir/modifier notes       │
│                                                               │
│  ADMIN (Chef Département)    DIRECTION                       │
│  ├─ Valider inscriptions     ├─ Vue globale statistiques    │
│  ├─ Gérer filières           ├─ Dashboard décisionnel       │
│  └─ Gérer modules            └─ Rapports consolidés         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Choix Techniques

### Stack Technique

**Backend : Django REST Framework**

- **Framework** : Django 5.0.2
- **API** : Django REST Framework 3.14.0
- **Authentification** : djangorestframework-simplejwt (JWT)
- **CORS** : django-cors-headers
- **Documentation** : drf-spectacular (Swagger)
- **Base de données** : SQLite (base par défaut Django)
- **ORM** : Django ORM

**Justification du choix Django REST :**

✅ **Batteries Included** : Admin, ORM, migrations, authentification intégrés  
✅ **Sécurité** : Protection CSRF, SQL injection, XSS par défaut  
✅ **Productivité** : Développement rapide avec code minimal  
✅ **Écosystème** : Nombreux packages disponibles

**Frontend : React + Vite**

- **Framework** : React 18.2.0
- **Build Tool** : Vite 5.0
- **Routing** : React Router 6.x
- **HTTP Client** : Axios
- **UI Framework** : Tailwind CSS 3.x
- **Icons** : Lucide React
- **State Management** : Context API + useState/useEffect

**Justification du choix React :**

✅ **Composants réutilisables** : Modularité et maintenabilité  
✅ **Virtual DOM** : Performances optimales  
✅ **Écosystème mature** : Large communauté et documentation  
✅ **Vite** : Build ultra-rapide avec Hot Module Replacement

---

## 🎯 Fonctionnalités Principales

### Gestion des Acteurs (4 Rôles)

**ÉTUDIANT**
- Soumettre une candidature d'inscription
- Consulter ses candidatures (statut : EN_ATTENTE, VALIDÉE, REJETÉE)
- Consulter ses notes par module
- Voir la liste des filières disponibles

**ENSEIGNANT**
- Consulter ses modules assignés
- Voir la liste des étudiants inscrits par module
- Saisir et modifier les notes (contrôle, examen)
- Calcul automatique de la note finale (40% contrôle + 60% examen)

**ADMINISTRATEUR** (Chef de Département)
- Valider ou rejeter les candidatures d'inscription
- Gérer les filières (création, modification)
- Gérer les modules (assignation enseignants, volume horaire)
- Consulter l'historique des inscriptions

**DIRECTION**
- Dashboard avec statistiques globales
- Indicateurs clés : nombre d'étudiants, enseignants, départements
- Statistiques des candidatures (en attente, validées, rejetées)
- Rapports par filière et département

### Workflow Principal

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Étudiant   │      │     Admin    │      │ Enseignant  │
│             │      │              │      │             │
│ 1. Soumet   │      │ 2. Valide/   │      │ 3. Saisit   │
│ candidature │─────►│    Rejette   │─────►│    notes    │
│             │      │              │      │             │
└─────────────┘      └──────────────┘      └─────────────┘
       │                    │                      │
       │                    │                      │
       ▼                    ▼                      ▼
┌──────────────────────────────────────────────────────┐
│           Base de Données Centralisée (SQLite)       │
│  • Départements  • Filières  • Modules               │
│  • Inscriptions  • Notes     • Utilisateurs          │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
                  ┌─────────────┐
                  │  Direction  │
                  │             │
                  │ 4. Consulte │
                  │ statistiques│
                  └─────────────┘
```

---

## 📚 Documentation API

### Documentation Interactive Swagger

**URL :** `http://localhost:8000/api/schema/swagger-ui/`

La documentation Swagger permet de :
- ✅ Visualiser tous les endpoints disponibles
- ✅ Tester les requêtes directement dans le navigateur
- ✅ Voir les schémas de requête/réponse
- ✅ S'authentifier avec JWT pour tester les endpoints protégés

### Endpoints Principaux

#### Authentification

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/api/auth/login/` | Connexion (obtenir JWT) | Non |
| POST | `/api/auth/register/` | Inscription étudiant | Non |
| POST | `/api/auth/refresh/` | Rafraîchir access token | Non |

#### Inscriptions (Candidatures)

| Méthode | Endpoint | Description | Rôle |
|---------|----------|-------------|------|
| GET | `/api/inscriptions/` | Liste toutes inscriptions | Admin, Direction |
| POST | `/api/inscriptions/` | Créer candidature | Étudiant |
| GET | `/api/inscriptions/my_inscriptions/` | Mes candidatures | Étudiant |
| GET | `/api/inscriptions/pending/` | Candidatures en attente | Admin |
| POST | `/api/inscriptions/{id}/validate/` | Valider/Rejeter | Admin |

#### Notes

| Méthode | Endpoint | Description | Rôle |
|---------|----------|-------------|------|
| GET | `/api/notes/my_modules/` | Mes modules | Enseignant |
| GET | `/api/notes/students_by_module/` | Étudiants d'un module | Enseignant |
| POST | `/api/notes/bulk_update_grades/` | Saisir notes en masse | Enseignant |

#### Statistiques

| Méthode | Endpoint | Description | Rôle |
|---------|----------|-------------|------|
| GET | `/api/statistics/dashboard/` | Stats globales | Direction |

---

## 🛠️ Technologies Utilisées

### Backend

- **Python** 3.10
- **Django** 5.0.2
- **Django REST Framework** 3.14.0
- **SQLite** (base de données intégrée)
- **JWT** (djangorestframework-simplejwt)
- **Swagger** (drf-spectacular)

### Frontend

- **React** 18.2.0
- **Vite** 5.0
- **React Router** 6.x
- **Axios** (client HTTP)
- **Tailwind CSS** 3.x
- **Lucide Icons**

---

## 📊 Métriques du Projet

- **Nombre d'endpoints API** : 28
- **Nombre de modèles** : 6 (User, Departement, Filiere, Module, Inscription, Note)
- **Nombre de pages frontend** : 15+
- **Base de données** : SQLite (fichier unique `db.sqlite3`)

---

**Projet développé dans le cadre académique**

*Plateforme de transformation digitale pour l'enseignement supérieur*