import { useQuery } from "@tanstack/react-query";
import { 
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
    PieChart, Pie, Cell, Legend 
} from 'recharts';
import { 
    Users, GraduationCap, Building2, BookOpen, 
    TrendingUp, Activity, AlertCircle, Loader2, Clock,
    Maximize, Filter as FilterIcon 
} from "lucide-react";
import api from "../../services/api"; // Ensure this path matches your project structure

const COLORS = ['#0ea5e9', '#22c55e', '#eab308', '#ef4444', '#8b5cf6'];

export default function Stats() {
    
    // 1. Fetch Data
    const { data: stats, isLoading, isError } = useQuery({
        queryKey: ['directionStats'],
        queryFn: async () => {
            const res = await api.get('/admin/dashboard/');
            return res.data;
        }
    });

    if (isLoading) return <LoadingState />;
    if (isError) return <ErrorState />;

    // 2. Prepare Data
    const kpis = stats?.kpi || [];
    const trends = stats?.enrollment_trends || [];
    const deptDist = stats?.department_dist || [];

    // 3. Helper: Icon Mapper
    const getIcon = (name) => {
        const icons = { 
            Users, 
            Clock,      // Dossiers en Attente
            Maximize,   // Taux de Remplissage
            Filter: FilterIcon, // Taux d'Admission
            BookOpen,
            TrendingUp,
            GraduationCap
        };
        const Icon = icons[name] || Activity;
        return <Icon className="w-6 h-6 text-white" />;
    };

    // 4. Helper: Color Mapper (Backgrounds for Icons)
    const getColorClass = (colorName) => {
        const colors = {
            blue: "bg-blue-500 shadow-blue-200",
            amber: "bg-amber-500 shadow-amber-200",
            emerald: "bg-emerald-500 shadow-emerald-200",
            purple: "bg-purple-500 shadow-purple-200",
            red: "bg-red-500 shadow-red-200",
        };
        return colors[colorName] || "bg-slate-500 shadow-slate-200";
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-slate-900">Statistiques Globales</h1>
                <p className="text-slate-500 mt-1">Indicateurs de performance et santé de l'établissement.</p>
            </div>

            {/* KPI Cards Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {kpis.map((kpi, idx) => (
                    <div key={idx} className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 relative overflow-hidden group hover:shadow-md transition-shadow duration-300">
                        <div className="flex justify-between items-start z-10 relative">
                            <div>
                                <p className="text-sm font-medium text-slate-500 mb-1 uppercase tracking-wide">{kpi.label}</p>
                                <h3 className="text-3xl font-bold text-slate-900 mt-2">{kpi.value}</h3>
                            </div>
                            <div className={`p-3 rounded-lg shadow-lg ${getColorClass(kpi.color)}`}>
                                {getIcon(kpi.icon)}
                            </div>
                        </div>
                        {/* Decorative Background Circle */}
                        <div className={`absolute -bottom-6 -right-6 w-24 h-24 rounded-full opacity-10 transition-transform duration-300 group-hover:scale-110 ${kpi.color === 'blue' ? 'bg-blue-500' : kpi.color === 'amber' ? 'bg-amber-500' : kpi.color === 'emerald' ? 'bg-emerald-500' : 'bg-purple-500'}`} />
                    </div>
                ))}
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                
                {/* Chart 1: Enrollment Trends */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-blue-500" />
                        Tendance des Inscriptions
                    </h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b'}} dy={10} />
                                <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                                <Tooltip 
                                    cursor={{fill: '#f8fafc'}}
                                    contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}
                                />
                                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={50} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Chart 2: Department Distribution */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                        <Building2 className="w-5 h-5 text-emerald-500" />
                        Poids des Départements
                    </h3>
                    <div className="h-80 relative">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={deptDist}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={80}
                                    outerRadius={110}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {deptDist.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                                <Legend verticalAlign="bottom" height={36} iconType="circle" />
                            </PieChart>
                        </ResponsiveContainer>
                        
                        {/* Donut Center Label */}
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none pb-8">
                            <div className="text-center">
                                <p className="text-xs text-slate-400 font-medium uppercase">Total</p>
                                <p className="text-3xl font-bold text-slate-800">
                                    {deptDist.reduce((acc, curr) => acc + curr.value, 0)}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Utility Components
const LoadingState = () => (
    <div className="h-96 flex flex-col items-center justify-center text-slate-400 gap-3">
        <Loader2 className="w-10 h-10 animate-spin text-blue-600" />
        <p>Chargement des indicateurs stratégiques...</p>
    </div>
);

const ErrorState = () => (
    <div className="p-6 bg-red-50 text-red-700 rounded-xl flex items-center gap-3 border border-red-100">
        <AlertCircle className="w-6 h-6" />
        <div>
            <p className="font-bold">Erreur de connexion</p>
            <p className="text-sm">Impossible de récupérer les statistiques en temps réel.</p>
        </div>
    </div>
);