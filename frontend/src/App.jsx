import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute'; 

import Login from './pages/auth/Login';
import AdminDashboard from "./pages/espace-admin/AdminDashboard";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Stats from "./pages/espace-direction/Stats";
import Rapports from "./pages/espace-direction/Rapports";
import Performance from "./pages/espace-direction/Performance";
const queryClient = new QueryClient();
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
    <QueryClientProvider client={queryClient}>
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
<Route path="/admin/validations" element={<AdminDashboard />} />        
    </Route>

            {/* SECURITY: Only Direction */}
            <Route element={<ProtectedRoute allowedRoles={['DIRECTION', 'ADMIN']} />}>
              <Route path="/direction/stats" element={<AdminDashboard />} />
              <Route path="/direction/stats" element={<Stats />} />
<Route path="/direction/rapports" element={<Rapports />} />
<Route path="/direction/performance" element={<Performance />} />
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;