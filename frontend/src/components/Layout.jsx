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
  ChevronRight,
  ChevronLeft, // Added this for the toggle button
  BookOpen,
  FilePlus,      
  FileCheck,     
  FileBarChart,  
  Library,       
  PieChart,      
  Award
} from 'lucide-react';

const Layout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  // State for Mobile Menu (Open/Close)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  // State for Desktop Sidebar (Minimized/Full)
  const [isCollapsed, setIsCollapsed] = useState(false);

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
          setIsSidebarOpen(false);
        }}
        title={isCollapsed ? label : ""} // Shows tooltip when minimized
        className={`
            flex items-center gap-3 rounded-lg py-3 font-medium transition-all duration-300
            ${isCollapsed ? 'justify-center px-2 w-full' : 'px-4 w-full'}
            ${isActive 
            ? 'bg-blue-600 text-white shadow-md' 
            : 'text-gray-400 hover:bg-gray-800 hover:text-white'}
        `}
      >
        {/* Icon (Fixed size) */}
        <Icon size={20} className="min-w-[20px]" />
        
        {/* Label (Hidden when collapsed) */}
        {!isCollapsed && (
            <span className="truncate animate-in fade-in duration-200">{label}</span>
        )}

        {/* Active Indicator Arrow (Hidden when collapsed) */}
        {!isCollapsed && isActive && <ChevronRight size={16} className="ml-auto opacity-70" />}
      </button>
    );
  };

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      
      {/* 1. SIDEBAR */}
      <aside 
        className={`
            fixed inset-y-0 left-0 z-50 transform bg-[#1C2434] text-white transition-all duration-300 ease-in-out 
            ${isSidebarOpen ? 'translate-x-0 w-64' : '-translate-x-full'} 
            lg:static lg:translate-x-0 
            ${isCollapsed ? 'lg:w-20' : 'lg:w-64'}
        `}
      >
        {/* Header: Logo + Toggle Button */}
        <div className={`flex h-20 items-center border-b border-gray-800 ${isCollapsed ? 'justify-center' : 'justify-between px-6'}`}>
          
          {/* Logo Logic */}
          {!isCollapsed ? (
             <h1 className="text-2xl font-bold tracking-wider truncate">
               ACADEMIYA<span className="text-blue-500">.</span>
             </h1>
          ) : (
             <h1 className="text-xl font-bold text-blue-500">AH</h1>
          )}

          {/* Toggle Button (Desktop Only) */}
          <button 
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="hidden lg:block text-gray-400 hover:text-white focus:outline-none"
          >
            {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
          </button>

          {/* Close Button (Mobile Only) */}
          <button onClick={() => setIsSidebarOpen(false)} className="lg:hidden">
            <X size={24} className="text-gray-400" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="mt-5 px-3 pb-20 overflow-y-auto h-[calc(100vh-160px)] scrollbar-hide space-y-2">
          
         {/* DASHBOARD LINK */}
          <MenuItem 
            icon={user?.role === 'DIRECTION' ? PieChart : LayoutDashboard} 
            label={
                user?.role === 'DIRECTION' ? 'Pilotage Stratégique' : 
                user?.role === 'ADMIN' ? 'Tableau de Bord' :
                'Accueil'
            }            
            path={
               user?.role === 'ETUDIANT' ? '/etudiant/dashboard' :
               user?.role === 'ENSEIGNANT' ? '/enseignant/dashboard' :
               user?.role === 'ADMIN' ? '/admin/dashboard' :
               '/direction/stats'
            } 
          />

          {/* --- ESPACE ÉTUDIANT --- */}
          {user?.role === 'ETUDIANT' && (
            <>
              <MenuItem icon={FilePlus} label="Nouvelle Candidature" path="/etudiant/candidature" />
              <MenuItem icon={FileText} label="Mes Candidatures" path="/etudiant/inscriptions" />
              <MenuItem icon={GraduationCap} label="Mes Notes" path="/etudiant/notes" />
            </>
          )}

          {/* --- ESPACE ENSEIGNANT --- */}
          {user?.role === 'ENSEIGNANT' && (
            <>
              <MenuItem icon={BookOpen} label="Mes Modules" path="/enseignant/modules" />
            </>
          )}

          {/* --- ESPACE ADMIN --- */}
          {user?.role === 'ADMIN' && (
            <>
              <MenuItem icon={FileCheck} label="Validations" path="/admin/validations" />
              <MenuItem icon={Users} label="Toutes les Inscriptions" path="/admin/inscriptions" />
              <MenuItem icon={Library} label="Filières & Modules" path="/admin/filieres" />
            </>
          )}

          {/* --- ESPACE DIRECTION --- */}
          {user?.role === 'DIRECTION' && (
           <>
              <MenuItem icon={FileBarChart} label="Rapports & Listes" path="/direction/rapports" />
              <MenuItem icon={Award} label="Résultats & Examens" path="/direction/performance" />
            </>
          )}

        </nav>

        {/* Logout (Bottom Fixed) */}
        <div className="absolute bottom-0 w-full border-t border-gray-800 bg-[#1C2434] p-4">
          
          {/* User Info (Hidden when collapsed) */}
          {!isCollapsed && (
            <div className="mb-4 px-2 flex items-center gap-3 animate-in fade-in">
                <div className="h-8 w-8 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-sm">
                    {user?.username?.charAt(0).toUpperCase()}
                </div>
                <div className="overflow-hidden">
                    <p className="text-sm font-medium truncate">{user?.username}</p>
                    <p className="text-xs text-gray-500 truncate capitalize">{user?.role?.toLowerCase()}</p>
                </div>
            </div>
          )}

          <button 
            onClick={handleLogout}
            title={isCollapsed ? "Déconnexion" : ""}
            className={`
                flex w-full items-center gap-3 rounded-lg py-2 text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-colors
                ${isCollapsed ? 'justify-center px-0' : 'px-4'}
            `}
          >
            <LogOut size={20} />
            {!isCollapsed && <span>Déconnexion</span>}
          </button>
        </div>
      </aside>

      {/* 2. MAIN CONTENT AREA */}
      <div className="flex flex-1 flex-col overflow-hidden transition-all duration-300">
        
        {/* Header */}
        <header className="flex h-20 items-center justify-between bg-white px-8 shadow-sm border-b border-gray-200">
          <button onClick={() => setIsSidebarOpen(true)} className="rounded-md border p-2 text-gray-600 lg:hidden">
            <Menu size={24} />
          </button>

          <div className="hidden sm:block">
            <h2 className="text-xl font-bold text-slate-800 tracking-tight">
              Espace {user?.role === 'DIRECTION' ? 'Direction' : 
                      user?.role === 'ADMIN' ? 'Administration' : 
                      user?.role === 'ENSEIGNANT' ? 'Enseignant' : 
                      'Étudiant'}
            </h2>
          </div>

          <div className="flex items-center gap-4">
            {/* User Avatar in Header (Only visible if sidebar is collapsed for better UX) */}
            {isCollapsed && (
                 <div className="h-8 w-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-sm">
                    {user?.username?.charAt(0).toUpperCase()}
                 </div>
            )}
          </div>
        </header>

        {/* Scrollable Page Content */}
        <main className="flex-1 overflow-y-auto overflow-x-hidden bg-slate-50 p-6 md:p-8">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;