import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute'; // Import it
import Login from './pages/auth/Login';

// Mock Pages
const StudentDash = () => <h1>Dashboard Etudiant</h1>;
const AdminDash = () => <h1>Admin Validation</h1>;
const StatsDash = () => <h1>Direction Stats</h1>;
const StudentCandidature = () => <h1>Ma Candidature</h1>;
const TeacherDashboard = () => <h1>Espace Enseignant - Dashboard</h1>;
const TeacherModules = () => <h1>Mes Modules</h1>;
const TeacherGrades = () => <h1>Saisie des Notes</h1>;



function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />

          {/* WRAPPER: Layout (Navbar/Sidebar) */}
          <Route element={<Layout />}>
            <Route path="/" element={<h1>Accueil</h1>} />

            {/* SECURITY: Only Students */}
            <Route element={<ProtectedRoute allowedRoles={['ETUDIANT']} />}>
              <Route path="/etudiant/dashboard" element={<StudentDash />} />
                            <Route path="/etudiant/candidature" element={<StudentCandidature />} />  {/* ← ADD THIS */}

            </Route>
            // Add teacher routes in the Routes section:
<Route element={<ProtectedRoute allowedRoles={['ENSEIGNANT']} />}>
  <Route path="/enseignant/dashboard" element={<TeacherDashboard />} />
  <Route path="/enseignant/modules" element={<TeacherModules />} />
  <Route path="/enseignant/notes/:moduleId" element={<TeacherGrades />} />
</Route>

            {/* SECURITY: Only Admins */}
            <Route element={<ProtectedRoute allowedRoles={['ADMIN', 'DIRECTION']} />}>
              <Route path="/admin/validations" element={<AdminDash />} />
            </Route>

            {/* SECURITY: Only Direction */}
            <Route element={<ProtectedRoute allowedRoles={['DIRECTION', 'ADMIN']} />}>
              <Route path="/direction/stats" element={<StatsDash />} />
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;