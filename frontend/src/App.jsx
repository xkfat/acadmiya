import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute'; // Import it
import Login from './pages/auth/Login';

// Mock Pages
const StudentDash = () => <h1>Dashboard Etudiant</h1>;
const AdminDash = () => <h1>Admin Validation</h1>;
const StatsDash = () => <h1>Direction Stats</h1>;

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