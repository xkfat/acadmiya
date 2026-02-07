import { useState, useMemo } from 'react';
import { useQuery } from "@tanstack/react-query";
import { 
    FileSpreadsheet, FileText, Search, Printer, 
    Filter, Loader2, AlertCircle, Building2, BookOpen 
} from "lucide-react";
import api from "../../services/api";

// --- ROBUST PDF IMPORTS ---
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable"; // Safer import for Vite
import * as XLSX from "xlsx";

export default function Rapports() {
    // --- 1. STATES ---
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedDept, setSelectedDept] = useState("ALL");
    const [selectedFiliere, setSelectedFiliere] = useState("ALL");
    const [selectedStatus, setSelectedStatus] = useState("ALL");
    const [selectedYear, setSelectedYear] = useState("ALL");

    // --- 2. FETCH DATA ---
    const { data: inscriptions = [], isLoading } = useQuery({
        queryKey: ['allInscriptions'],
        queryFn: async () => {
            const res = await api.get('/inscriptions/');
            return res.data;
        }
    });

    // --- 3. DYNAMIC DROPDOWNS ---
    const departments = useMemo(() => [...new Set(inscriptions.map(i => i.departement_name).filter(Boolean))], [inscriptions]);
    
    const filieres = useMemo(() => {
        let filtered = inscriptions;
        if (selectedDept !== "ALL") filtered = filtered.filter(i => i.departement_name === selectedDept);
        return [...new Set(filtered.map(i => i.filiere_name).filter(Boolean))];
    }, [inscriptions, selectedDept]);

    const years = useMemo(() => [...new Set(inscriptions.map(i => i.academic_year).filter(Boolean))], [inscriptions]);

    // --- 4. FILTERING LOGIC ---
    const filteredData = inscriptions.filter(item => {
        const matchesSearch = (item.student_name || "").toLowerCase().includes(searchTerm.toLowerCase());
        const matchesDept = selectedDept === "ALL" || item.departement_name === selectedDept;
        const matchesFiliere = selectedFiliere === "ALL" || item.filiere_name === selectedFiliere;
        const matchesStatus = selectedStatus === "ALL" || item.status === selectedStatus;
        const matchesYear = selectedYear === "ALL" || item.academic_year === selectedYear;

        return matchesSearch && matchesDept && matchesFiliere && matchesStatus && matchesYear;
    });

    // --- 5. SMART COLUMNS (Hide 'Date' if Pending) ---
    const showDateColumn = selectedStatus !== 'PENDING';

    // --- 6. PDF EXPORT ---
    const exportPDF = () => {
        const doc = new jsPDF();
        
        // Header
        doc.setFontSize(10);
        doc.setTextColor(100);
        
        doc.setFontSize(18);
      //  doc.setTextColor(153, 27, 27); // Dark Red Title
        doc.setFont("helvetica", "bold");
        doc.text("ACADEMIYA-HUB", 14, 25);
        
        doc.setFontSize(12);
        doc.setTextColor(0);
        doc.text("Liste des Inscriptions", 14, 35);

        // Dynamic Columns for PDF
        let tableHeaders = ["Étudiant", "Filière", "Statut", "Année"];
        if (showDateColumn) tableHeaders.push("Date Validation");

        const tableRows = filteredData.map(row => {
            let rowData = [
                row.student_name,
                row.filiere_name,
                row.status === 'VALIDATED' ? 'ADMIS' : row.status === 'REJECTED' ? 'REFUSÉ' : 'EN ATTENTE',
                row.academic_year
            ];
            if (showDateColumn) {
                rowData.push(row.validation_date ? new Date(row.validation_date).toLocaleDateString('fr-FR') : "-");
            }
            return rowData;
        });

        autoTable(doc, {
            head: [tableHeaders],
            body: tableRows,
            startY: 45,
            theme: 'striped',
            headStyles: { fillColor: [28, 36, 52] }, // Dark Navy
            styles: { fontSize: 9 },
        });

        doc.save("Rapport_Academique.pdf");
    };

    // --- 7. EXCEL EXPORT ---
    const exportExcel = () => {
        const dataToExport = filteredData.map(row => {
            const item = {
                "Étudiant": row.student_name,
                "Filière": row.filiere_name,
                "Département": row.departement_name,
                "Statut": row.status,
                "Année": row.academic_year
            };
            if (showDateColumn) {
                item["Date Validation"] = row.validation_date;
            }
            return item;
        });

        const worksheet = XLSX.utils.json_to_sheet(dataToExport);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, "Données");
        XLSX.writeFile(workbook, "Export_Donnees.xlsx");
    };

    if (isLoading) return <div className="h-96 flex items-center justify-center text-slate-500 gap-2"><Loader2 className="animate-spin"/> Chargement...</div>;

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Rapports & Listes</h1>
                    <p className="text-slate-500 mt-1">Exportation des données académiques.</p>
                </div>
                <div className="flex gap-3">
                    <button onClick={exportExcel} className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium shadow-sm transition-all">
                        <FileSpreadsheet className="w-4 h-4" /> Excel
                    </button>
                    {/* DARK RED BUTTON */}
                    <button onClick={exportPDF} className="flex items-center gap-2 px-4 py-2 bg-[#991B1B] hover:bg-red-900 text-white rounded-lg font-medium shadow-sm transition-all">
                        <Printer className="w-4 h-4" /> PDF
                    </button>
                </div>
            </div>

            {/* --- FILTERS --- */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center gap-2 text-slate-800 font-bold mb-2">
                    <Filter className="w-4 h-4" /> Filtres
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                    {/* Search */}
                    <div className="relative lg:col-span-2">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
                        <input 
                            type="text" 
                            placeholder="Rechercher..." 
                            className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-slate-50"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>

                    {/* Department Select */}
                    <div className="relative">
                        <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
                        <select 
                            className="w-full pl-10 pr-8 py-2 rounded-lg border border-slate-200 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none text-sm"
                            value={selectedDept}
                            onChange={(e) => { setSelectedDept(e.target.value); setSelectedFiliere("ALL"); }}
                        >
                            <option value="ALL">Tous Départements</option>
                            {departments.map(d => <option key={d} value={d}>{d}</option>)}
                        </select>
                    </div>

                    {/* Filiere Select */}
                    <div className="relative">
                        <BookOpen className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
                        <select 
                            className="w-full pl-10 pr-8 py-2 rounded-lg border border-slate-200 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none text-sm"
                            value={selectedFiliere}
                            onChange={(e) => setSelectedFiliere(e.target.value)}
                        >
                            <option value="ALL">Toutes Filières</option>
                            {filieres.map(f => <option key={f} value={f}>{f}</option>)}
                        </select>
                    </div>

                    {/* Status Select */}
                    <div className="relative">
                        <AlertCircle className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
                        <select 
                            className="w-full pl-10 pr-8 py-2 rounded-lg border border-slate-200 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none text-sm"
                            value={selectedStatus}
                            onChange={(e) => setSelectedStatus(e.target.value)}
                        >
                            <option value="ALL">Tous Statuts</option>
                            <option value="VALIDATED">Admis</option>
                            <option value="PENDING">En Attente</option>
                            <option value="REJECTED">Refusé</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* --- RESULT COUNT & TABLE --- */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                {/* Result Count Line - Right Side, Black, Simple */}
                {(searchTerm || selectedDept !== "ALL" || selectedStatus !== "ALL") && (
                    <div className="px-6 py-3 border-b border-slate-100 flex justify-end">
                        <span className="text-sm font-medium text-black">
                            Total : {filteredData.length} dossier{filteredData.length > 1 ? 's' : ''}
                        </span>
                    </div>
                )}

                <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50 border-b border-slate-200">
                        <tr>
                            <th className="px-6 py-4 font-bold text-slate-700">Étudiant</th>
                            <th className="px-6 py-4 font-bold text-slate-700">Formation</th>
                            <th className="px-6 py-4 font-bold text-slate-700">Année</th>
                            <th className="px-6 py-4 font-bold text-slate-700">État</th>
                            {/* Conditionally hide header */}
                            {showDateColumn && (
                                <th className="px-6 py-4 font-bold text-slate-700">Date Validation</th>
                            )}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {filteredData.length === 0 ? (
                            <tr><td colSpan={showDateColumn ? 5 : 4} className="p-8 text-center text-slate-500 bg-slate-50">Aucun résultat.</td></tr>
                        ) : (
                            filteredData.map((row) => (
                                <tr key={row.id} className="hover:bg-blue-50/50 transition-colors">
                                    <td className="px-6 py-4 font-semibold text-slate-900">{row.student_name}</td>
                                    <td className="px-6 py-4">
                                        <div className="text-slate-900">{row.filiere_name}</div>
                                        <div className="text-xs text-slate-500">{row.departement_name}</div>
                                    </td>
                                    <td className="px-6 py-4 text-slate-600 font-mono">{row.academic_year}</td>
                                    <td className="px-6 py-4">
                                        <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-bold border ${
                                            row.status === 'VALIDATED' ? 'bg-green-100 text-green-700 border-green-200' :
                                            row.status === 'REJECTED' ? 'bg-red-100 text-red-700 border-red-200' :
                                            'bg-amber-100 text-amber-700 border-amber-200'
                                        }`}>
                                            {row.status === 'VALIDATED' ? 'ADMIS' : 
                                             row.status === 'REJECTED' ? 'REFUSÉ' : 'EN ATTENTE'}
                                        </span>
                                    </td>
                                    {/* Conditionally hide cell */}
                                    {showDateColumn && (
                                        <td className="px-6 py-4 text-slate-500">
                                            {row.validation_date ? new Date(row.validation_date).toLocaleDateString('fr-FR') : "-"}
                                        </td>
                                    )}
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}