import { useQuery } from "@tanstack/react-query";
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts';
import { Users, BookOpen, GraduationCap, TrendingUp, Loader2, AlertCircle } from "lucide-react";
import api from "../../services/api"; 

const COLORS = ['#2563eb', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6'];

export default function AdminDashboard() {
    
    // 1. FETCH DATA (Using 'api' so the token is attached automatically)
    const { data: dashboardData, isLoading, isError } = useQuery({
        queryKey: ['adminDashboard'],
        queryFn: async () => {
            const response = await api.get('/admin/dashboard/');
            return response.data;
        },
        retry: 1
    });

    // 2. LOADING STATE
    if (isLoading) {
        return (
            <div className="flex h-96 w-full items-center justify-center flex-col gap-4">
                <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
                <p className="text-slate-500">Chargement des statistiques...</p>
            </div>
        );
    }

    // 3. ERROR STATE
    if (isError) {
        return (
            <div className="p-6 m-6 bg-red-50 border border-red-200 rounded-xl flex items-center gap-4 text-red-700">
                <AlertCircle className="h-6 w-6" />
                <div>
                    <p className="font-bold">Erreur de chargement</p>
                    <p className="text-sm">Impossible de récupérer les données. Vérifiez que vous êtes connecté en tant qu'administrateur.</p>
                </div>
            </div>
        );
    }

    // 4. PREPARE REAL DATA (Fallback to empty arrays if data is missing)
    // We map the string icon names from backend to real React components
    const rawStats = dashboardData?.kpi || [];
    const stats = rawStats.map(stat => ({
        ...stat,
        icon: stat.icon === 'Users' ? Users : 
              stat.icon === 'BookOpen' ? BookOpen : 
              stat.icon === 'GraduationCap' ? GraduationCap : TrendingUp
    }));

    const enrollmentData = dashboardData?.enrollment_trends || [];
    const departmentData = dashboardData?.department_dist || [];

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex flex-col gap-1">
                <h1 className="text-3xl font-bold tracking-tight text-slate-900">Tableau de Bord</h1>
                <p className="text-slate-500">Vue d'ensemble de ACADEMIYATI.</p>
            </div>

            {/* KPI Cards */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                {stats.map((stat, index) => (
                    <div key={index} className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-slate-500">{stat.label}</p>
                                <p className="text-2xl font-bold mt-1 text-slate-900">{stat.value}</p>
                            </div>
                            <div className="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center text-blue-600">
                                <stat.icon className="w-5 h-5" />
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Charts Area */}
            <div className="grid gap-6 md:grid-cols-2">
                {/* Bar Chart */}
                <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
                    <h3 className="text-lg font-semibold mb-6 text-slate-800">Inscriptions par Mois</h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={enrollmentData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                                <XAxis dataKey="name" fontSize={12} tickLine={false} axisLine={false} stroke="#64748b" />
                                <YAxis fontSize={12} tickLine={false} axisLine={false} stroke="#64748b" />
                                <Tooltip 
                                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                                    cursor={{ fill: '#f1f5f9' }}
                                />
                                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={40} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Pie Chart */}
                <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
                    <h3 className="text-lg font-semibold mb-6 text-slate-800">Étudiants par Département</h3>
                    <div className="h-[300px] w-full flex items-center justify-center">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={departmentData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={100}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {departmentData.map((_entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                    {/* Custom Legend */}
                    <div className="flex justify-center gap-4 mt-4 flex-wrap">
                        {departmentData.map((entry, index) => (
                            <div key={entry.name} className="flex items-center gap-2 text-xs font-medium">
                                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }}></div>
                                <span className="text-slate-600">{entry.name}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}