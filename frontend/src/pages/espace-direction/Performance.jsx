import { useQuery } from "@tanstack/react-query";
import { 
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell 
} from 'recharts';
import { 
    Award, TrendingUp, AlertTriangle, CheckCircle2, Loader2, Trophy 
} from "lucide-react";
import api from "../../services/api";

export default function Performance() {
    
    const { data: stats, isLoading } = useQuery({
        queryKey: ['academicPerformance'],
        queryFn: async () => {
            const res = await api.get('/admin/performance/'); // On ajoutera l'URL après
            return res.data;
        }
    });

    if (isLoading) return (
        <div className="h-96 flex items-center justify-center text-slate-500 gap-2">
            <Loader2 className="animate-spin text-blue-600"/> Chargement des résultats...
        </div>
    );

    const chartData = stats?.chart_data || [];
    const topStudents = stats?.top_students || [];

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-slate-900">Résultats & Examens</h1>
                <p className="text-slate-500 mt-1">Analyse de la performance académique et palmarès.</p>
            </div>

            {/* Top Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
                    <div>
                        <p className="text-sm font-medium text-slate-500 uppercase">Moyenne Générale</p>
                        <h3 className="text-4xl font-bold text-slate-900 mt-2">{stats?.global_average || 0}<span className="text-xl text-slate-400">/20</span></h3>
                    </div>
                    <div className="p-4 bg-blue-50 text-blue-600 rounded-full">
                        <TrendingUp className="w-8 h-8" />
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
                    <div>
                        <p className="text-sm font-medium text-slate-500 uppercase">Taux de Réussite</p>
                        <h3 className="text-4xl font-bold text-emerald-600 mt-2">{stats?.success_rate || 0}<span className="text-xl text-emerald-400">%</span></h3>
                    </div>
                    <div className="p-4 bg-emerald-50 text-emerald-600 rounded-full">
                        <CheckCircle2 className="w-8 h-8" />
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Graphique: Moyenne par Filière */}
                <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                        <Award className="w-5 h-5 text-amber-500" />
                        Moyennes par Filière
                    </h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                                <XAxis type="number" domain={[0, 20]} hide />
                                <YAxis dataKey="name" type="category" width={100} tick={{fontSize: 12}} />
                                <Tooltip 
                                    cursor={{fill: '#f8fafc'}}
                                    contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}
                                />
                                <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={30}>
                                    {chartData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.value >= 12 ? '#3b82f6' : '#ef4444'} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Liste: Top 5 Étudiants */}
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                        <Trophy className="w-5 h-5 text-amber-400" />
                        Majors de Promotion
                    </h3>
                    <div className="space-y-4">
                        {topStudents.length === 0 ? (
                            <p className="text-slate-500 text-center py-4">Aucune note enregistrée.</p>
                        ) : (
                            topStudents.map((student, idx) => (
                                <div key={idx} className="flex items-center gap-4 p-3 hover:bg-slate-50 rounded-lg transition-colors">
                                    <div className={`
                                        w-8 h-8 flex items-center justify-center rounded-full font-bold text-sm
                                        ${idx === 0 ? 'bg-amber-100 text-amber-700' : 
                                          idx === 1 ? 'bg-slate-200 text-slate-700' : 
                                          idx === 2 ? 'bg-orange-100 text-orange-800' : 'bg-slate-100 text-slate-500'}
                                    `}>
                                        {idx + 1}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-semibold text-slate-900 truncate">{student.name}</p>
                                        <p className="text-xs text-slate-500 truncate">{student.filiere}</p>
                                    </div>
                                    <div className="text-sm font-bold text-blue-600">
                                        {student.average}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}