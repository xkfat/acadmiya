import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, 
  GraduationCap, 
  Users, 
  FileText, 
  LogOut, 
  Menu, 
  X, 
  BarChart3,
  ChevronRight
} from 'lucide-react';

const Layout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Helper for Menu Items
  const MenuItem = ({ icon: Icon, label, path }) => {
    const isActive = location.pathname === path;
    return (
      <button
        onClick={() => {
          navigate(path);
          setIsSidebarOpen(false); // Close mobile menu on click
        }}
        className={`flex w-full items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-colors
        ${isActive 
          ? 'bg-primary text-white shadow-md' 
          : 'text-gray-400 hover:bg-gray-800 hover:text-white'
        }`}
      >
        <Icon size={20} />
        <span>{label}</span>
        {isActive && <ChevronRight size={16} className="ml-auto" />}
      </button>
    );
  };

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      
      {/* 1. SIDEBAR (Fixed) */}
      <aside 
        className={`fixed inset-y-0 left-0 z-50 w-64 transform bg-[#1C2434] text-white transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        {/* Logo */}
        <div className="flex h-20 items-center justify-between px-6">
          <h1 className="text-2xl font-bold tracking-wider">
            ACADEMIYA<span className="text-primary">.Hub</span>
          </h1>
          <button onClick={() => setIsSidebarOpen(false)} className="lg:hidden">
            <X size={24} className="text-gray-400" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="mt-5 px-4 space-y-2">
          <p className="px-4 text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">Menu</p>
          
          <MenuItem icon={LayoutDashboard} label="Accueil" path="/" />

          {/* ETUDIANT MENU */}
          {user?.role === 'ETUDIANT' && (
            <>
              <MenuItem icon={FileText} label="Ma Candidature" path="/etudiant/candidature" />
              <MenuItem icon={GraduationCap} label="Mon Espace" path="/etudiant/dashboard" />
            </>
          )}

          {/* ADMIN MENU */}
          {(user?.role === 'ADMIN' || user?.role === 'DIRECTION') && (
            <>
              <MenuItem icon={Users} label="Validations" path="/admin/validations" />
              <MenuItem icon={BarChart3} label="Statistiques" path="/direction/stats" />
            </>
          )}
        </nav>

        {/* Logout (Bottom) */}
        <div className="absolute bottom-0 w-full border-t border-gray-700 p-4">
          <button 
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-lg px-4 py-2 text-red-400 hover:bg-gray-800 hover:text-red-300 transition"
          >
            <LogOut size={20} />
            <span>Déconnexion</span>
          </button>
        </div>
      </aside>

      {/* 2. MAIN CONTENT AREA */}
      <div className="flex flex-1 flex-col overflow-hidden">
        
        {/* Header */}
        <header className="flex h-20 items-center justify-between bg-white px-6 shadow-sm">
          <button onClick={() => setIsSidebarOpen(true)} className="rounded-md border p-2 text-gray-600 lg:hidden">
            <Menu size={24} />
          </button>

          <div className="hidden sm:block">
            <h2 className="text-xl font-semibold text-gray-800">
              Espace {user?.role ? user.role.charAt(0) + user.role.slice(1).toLowerCase() : 'Invité'}
            </h2>
          </div>

          <div className="flex items-center gap-4">
            <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">
              {user?.username ? user.username.charAt(0).toUpperCase() : 'U'}
            </div>
          </div>
        </header>

        {/* Scrollable Page Content */}
        <main className="flex-1 overflow-y-auto overflow-x-hidden p-6 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;