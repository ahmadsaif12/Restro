import React from 'react';

type Props = {
    label: string;
    value: string;
    sub: string;
    icon: React.ReactNode;
    color: "emerald" | "blue" | "orange" | "green" | "purple";
};

const colorVariants: Record<string, string> = {
    emerald: "bg-[#10b981] shadow-emerald-200",
    blue: "bg-[#3b82f6] shadow-blue-200",
    orange: "bg-[#f97316] shadow-orange-200",
    green: "bg-[#22c55e] shadow-green-200",
    purple: "bg-[#a855f7] shadow-purple-200",
};

export default function StatCard({ label, value, sub, icon, color }: Props) {
    return (
        <div className="bg-white rounded-[24px] p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-all cursor-pointer group">
            <div className="flex justify-between items-start">
                <div className="space-y-4">
                    <span className="text-[13px] font-semibold text-slate-400 uppercase tracking-wider">{label}</span>
                    <div>
                        <div className="text-4xl font-extrabold text-slate-900 tracking-tight mb-1">{value}</div>
                        <div className="text-xs font-bold text-slate-400">{sub}</div>
                    </div>
                </div>
                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center text-white shadow-xl ${colorVariants[color] || colorVariants.blue}`}>
                    {icon}
                </div>
            </div>
        </div>
    );
}