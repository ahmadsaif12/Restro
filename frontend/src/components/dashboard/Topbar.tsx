"use client";

import { useEffect, useState, useRef } from "react";
import { useAuthStore } from "@/store/auth-store";
import { useRouter } from "next/navigation";
import {
    Calendar,
    Clock,
    Search,
    Bell,
    Settings,
    ChevronDown,
    Info,
    X,
    Activity,
    Volume2,
    VolumeX,
    ArrowRight,
    MoveVertical,
    CornerDownLeft,
    LayoutDashboard,
    TrendingUp,
    Monitor,
    ClipboardList,
    ChefHat,
    Pin,
    Utensils,
    QrCode,
    Package,
    BookOpen,
    BarChart2,
    Wallet,
    CreditCard,
    Users,
    Truck,
    TrendingDown,
    CheckCircle2
} from "lucide-react";

const navigationResults = [
    { icon: <LayoutDashboard size={16} />, label: "Dashboard", sub: "Navigate to dashboard", href: "/dashboard", color: "bg-blue-500", gradient: "from-cyan-500 to-blue-600" },
    { icon: <TrendingUp size={16} />, label: "Executive Dashboard", sub: "Navigate to executive dashboard", href: "/dashboard/executive", color: "bg-cyan-500", gradient: "from-blue-400 to-cyan-500" },
    { icon: <Monitor size={16} />, label: "POS", sub: "Navigate to pos", href: "/dashboard/pos", color: "bg-[#10b981]", gradient: "from-[#10b981] to-[#059669]" },
    { icon: <ClipboardList size={16} />, label: "Orders", sub: "Navigate to orders", href: "/dashboard/orders", color: "bg-orange-500", gradient: "from-orange-400 to-red-500" },
    { icon: <TrendingDown size={16} />, label: "Expenses", sub: "Navigate to expenses", href: "/dashboard/expenses", color: "bg-rose-500", gradient: "from-rose-400 to-red-600" },
    { icon: <Calendar size={16} />, label: "Calendar", sub: "Navigate to calendar", href: "/dashboard/calendar", color: "bg-[#10b981]", gradient: "from-[#10b981] to-[#059669]" },
    { icon: <CreditCard size={16} />, label: "Credit Management", sub: "Navigate to credit management", href: "/dashboard/credit", color: "bg-orange-500", gradient: "from-orange-400 to-orange-600" },
    { icon: <Truck size={16} />, label: "Vendor Management", sub: "Navigate to vendor management", href: "/dashboard/vendors", color: "bg-purple-500", gradient: "from-purple-400 to-indigo-600" },
    { icon: <Users size={16} />, label: "Staff Management", sub: "Navigate to staff management", href: "/dashboard/staff", color: "bg-blue-500", gradient: "from-blue-400 to-blue-600" },
];

export default function Topbar() {
    const [time, setTime] = useState("");
    const [date, setDate] = useState("");
    const [isLiveOpen, setIsLiveOpen] = useState(false);
    const [isSearchOpen, setIsSearchOpen] = useState(false);
    const [isSoundEnabled, setIsSoundEnabled] = useState(true);
    const [toast, setToast] = useState<{ show: boolean, message: string, sub: string } | null>(null);
    const [selectedIndex, setSelectedIndex] = useState(0);
    const { user } = useAuthStore();
    const router = useRouter();
    const liveRef = useRef<HTMLDivElement>(null);
    const searchRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        function tick() {
            const now = new Date();
            setTime(now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" }));
            setDate(now.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" }));
        }
        tick();
        const id = setInterval(tick, 1000);
        return () => clearInterval(id);
    }, []);

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (liveRef.current && !liveRef.current.contains(event.target as Node)) {
                setIsLiveOpen(false);
            }
            if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
                setIsSearchOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                setIsSearchOpen(true);
            }
            if (e.key === 'Escape') {
                setIsSearchOpen(false);
            }
            if (isSearchOpen) {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    setSelectedIndex(prev => (prev + 1) % navigationResults.length);
                }
                if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    setSelectedIndex(prev => (prev - 1 + navigationResults.length) % navigationResults.length);
                }
                if (e.key === 'Enter') {
                    router.push(navigationResults[selectedIndex].href);
                    setIsSearchOpen(false);
                }
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isSearchOpen, selectedIndex, router]);

    const toggleSound = () => {
        const newState = !isSoundEnabled;
        setIsSoundEnabled(newState);
        setToast({
            show: true,
            message: newState ? "Sound notifications enabled" : "Sound notifications disabled",
            sub: newState ? "You will now hear notification sounds" : "You will no longer hear notification sounds"
        });
        setTimeout(() => setToast(null), 3000);
    };

    return (
        <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-100 h-20 flex items-center gap-6 px-8">

            {/* Notification Toast */}
            {toast && (
                <div className="fixed top-6 right-6 z-[100] animate-in slide-in-from-right-4 fade-in duration-300">
                    <div className="bg-emerald-50 border border-emerald-100 rounded-2xl p-4 shadow-xl shadow-emerald-500/10 flex items-start gap-3 w-80">
                        <div className="mt-0.5 text-emerald-500 bg-white rounded-full p-0.5">
                            <CheckCircle2 size={20} fill="currentColor" className="text-white" />
                            <CheckCircle2 size={20} className="absolute inset-4.5 text-emerald-500" />
                            <CheckCircle2 size={20} />
                        </div>
                        <div>
                            <div className="text-sm font-bold text-emerald-800 leading-tight">{toast.message}</div>
                            <div className="text-[11px] text-emerald-600 font-medium mt-0.5">{toast.sub}</div>
                        </div>
                        <button onClick={() => setToast(null)} className="ml-auto text-emerald-300 hover:text-emerald-500 transition-colors">
                            <X size={16} />
                        </button>
                    </div>
                </div>
            )}

            {/* Greeting */}
            <div className="flex-1">
                <h1 className="font-bold text-xl text-slate-900 leading-tight tracking-tight">
                    Welcome back, {user?.full_name?.split(' ')[0] || "Saif"}! 👋
                </h1>
                <p className="text-xs text-slate-400 font-medium mt-0.5">{user?.role || "Owner / Proprietor"}</p>
            </div>

            {/* Date chip */}
            <div className="hidden lg:flex items-center gap-3 px-4 py-2.5 bg-orange-50/50 border border-orange-100 rounded-2xl shadow-sm shadow-orange-500/5">
                <div className="p-1.5 bg-orange-500 rounded-lg text-white">
                    <Calendar size={14} />
                </div>
                <div className="flex flex-col leading-none">
                    <span className="text-[10px] text-orange-600/60 font-bold uppercase tracking-wider">Date</span>
                    <span className="font-bold text-slate-800 text-xs mt-0.5">{date}</span>
                </div>
            </div>

            {/* Time chip */}
            <div className="hidden xl:flex items-center gap-3 px-4 py-2.5 bg-blue-50/50 border border-blue-100 rounded-2xl shadow-sm shadow-blue-500/5">
                <div className="p-1.5 bg-blue-500 rounded-lg text-white">
                    <Clock size={14} />
                </div>
                <div className="flex flex-col leading-none">
                    <span className="text-[10px] text-blue-600/60 font-bold uppercase tracking-wider">Time</span>
                    <span className="font-bold text-slate-800 text-xs mt-0.5 tabular-nums">{time}</span>
                </div>
            </div>

            {/* Live Indicator */}
            <div className="relative" ref={liveRef}>
                <button
                    onClick={() => setIsLiveOpen(!isLiveOpen)}
                    className={`flex items-center gap-2 border text-xs font-bold px-4 py-2.5 rounded-2xl transition-all ${isLiveOpen ? "bg-emerald-100 border-emerald-200 text-emerald-700 shadow-inner" : "bg-emerald-50 border-emerald-100 text-emerald-600 hover:bg-emerald-100 shadow-sm shadow-emerald-500/5"
                        }`}
                >
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    Live
                </button>

                {/* Real-time Status Popup */}
                {isLiveOpen && (
                    <>
                        <div
                            className="fixed inset-0 z-40 bg-transparent cursor-default"
                            onClick={() => setIsLiveOpen(false)}
                        ></div>
                        <div className="absolute top-full right-0 mt-3 w-72 bg-white rounded-3xl shadow-2xl border border-slate-100 overflow-hidden animate-in fade-in zoom-in duration-200 origin-top-right z-50">
                            <div className="bg-emerald-50/50 px-6 py-4 border-b border-emerald-100 flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                                    <span className="font-bold text-slate-800 text-sm">Real-time Status</span>
                                </div>
                                <Info size={14} className="text-slate-400" />
                            </div>
                            <div className="p-6 space-y-4">
                                <div className="flex items-center justify-between"><span className="text-xs text-slate-500 font-medium">Connection</span><span className="text-xs font-bold text-emerald-600 uppercase">Connected</span></div>
                                <div className="flex items-center justify-between bg-blue-50/50 p-3 rounded-xl border border-blue-100/50"><span className="text-xs text-blue-600 font-medium">Uptime</span><span className="text-xs font-bold text-blue-700">5m 18s</span></div>
                                <div className="flex items-center justify-between bg-purple-50/50 p-3 rounded-xl border border-purple-100/50"><span className="text-xs text-purple-600 font-medium">Total Events</span><span className="text-xs font-bold text-purple-700">0</span></div>
                                <div className="flex items-center justify-between bg-orange-50/50 p-3 rounded-xl border border-orange-100/50"><div className="flex items-center gap-2"><Activity size={12} className="text-orange-500" /><span className="text-xs text-orange-600 font-medium">Activity</span></div><span className="text-xs font-bold text-orange-700 uppercase">0/min</span></div>
                                <div className="pt-2 border-t border-slate-50 flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        {isSoundEnabled ? <Volume2 size={14} className="text-emerald-500" /> : <VolumeX size={14} className="text-slate-400" />}
                                        <span className="text-xs text-slate-600 font-medium">Sound Notifications</span>
                                    </div>
                                    <div
                                        onClick={toggleSound}
                                        className={`w-10 h-6 rounded-full relative cursor-pointer transition-colors duration-200 ${isSoundEnabled ? "bg-emerald-500" : "bg-slate-200"}`}
                                    >
                                        <div className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow-sm transition-all duration-200 ${isSoundEnabled ? "right-1" : "left-1"}`}></div>
                                    </div>
                                </div>
                            </div>
                            <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 text-[9px] text-center text-slate-400 font-bold uppercase tracking-widest">Real-time updates powered by WebSocket</div>
                        </div>
                    </>
                )}
            </div>

            {/* Search Dropdown Anchor */}
            <div className="relative" ref={searchRef}>
                <div
                    onClick={() => setIsSearchOpen(!isSearchOpen)}
                    className={`hidden md:flex items-center gap-3 bg-white border border-slate-200 rounded-2xl px-4 py-2.5 text-slate-400 w-64 cursor-text hover:border-slate-300 transition-all group shadow-sm ${isSearchOpen ? "ring-2 ring-orange-500/20 border-orange-500/40" : ""
                        }`}
                >
                    <Search size={16} className="group-hover:text-slate-600 transition-colors" />
                    <span className="flex-1 text-[11px] font-semibold tracking-tight">Search sections (⌘K)...</span>
                    <div className="bg-slate-100 px-1.5 py-0.5 rounded text-[9px] font-bold text-slate-400 border border-slate-200">Ctrl K</div>
                </div>

                {/* Quick Navigation Dropdown (Anchored) */}
                {isSearchOpen && (
                    <>
                        {/* Transparent backdrop to catch clicks anywhere */}
                        <div
                            className="fixed inset-0 z-40 bg-transparent cursor-default"
                            onClick={() => setIsSearchOpen(false)}
                        ></div>

                        <div className="absolute top-full right-0 mt-3 w-[330px] bg-white rounded-[32px] shadow-2xl border border-slate-100 overflow-hidden animate-in fade-in zoom-in duration-200 origin-top-right z-50">
                            {/* Dropdown Header with Search */}
                            <div className="flex items-center gap-3 px-5 py-4 border-b border-slate-50">
                                <Search className="text-blue-500" size={18} />
                                <input
                                    autoFocus
                                    type="text"
                                    placeholder="Search sections (⌘K)..."
                                    className="flex-1 bg-transparent border-none outline-none text-slate-800 font-bold text-xs placeholder:text-slate-400"
                                />
                                <div className="bg-slate-100 px-1.5 py-0.5 rounded text-[8px] font-black text-slate-400 border border-slate-200">Ctrl K</div>
                            </div>

                            {/* Navigation Hints */}
                            <div className="bg-slate-50/80 px-5 py-2.5 flex items-center gap-4 border-b border-slate-50">
                                <span className="text-[8px] font-black text-slate-400 uppercase tracking-[0.15em]">Quick Navigation</span>
                                <div className="flex items-center gap-2.5 ml-auto">
                                    <span className="flex items-center gap-1.5 text-[8px] font-bold text-slate-400 uppercase tracking-wider"><MoveVertical size={10} className="text-slate-300" /> Navigate</span>
                                    <span className="flex items-center gap-1.5 text-[8px] font-bold text-slate-400 uppercase tracking-wider"><kbd className="bg-white px-1 py-0.5 rounded border border-slate-200 text-[7px] font-black">Esc</kbd> Close</span>
                                </div>
                            </div>

                            {/* Results */}
                            <div className="max-h-[280px] overflow-y-auto py-1.5">
                                <div className="space-y-0.5 px-1.5">
                                    {navigationResults.map((item, index) => {
                                        const isSelected = index === selectedIndex;
                                        return (
                                            <div
                                                key={item.label}
                                                onMouseEnter={() => setSelectedIndex(index)}
                                                onClick={() => { router.push(item.href); setIsSearchOpen(false); }}
                                                className={`flex items-center gap-3 px-3 py-2.5 rounded-2xl cursor-pointer transition-all duration-200 group ${isSelected ? `bg-gradient-to-r ${item.gradient} shadow-lg shadow-blue-500/10` : "hover:bg-slate-50"
                                                    }`}
                                            >
                                                <div className={`w-8 h-8 rounded-xl flex items-center justify-center text-white shadow-sm shrink-0 ${isSelected ? "bg-white/20 backdrop-blur-sm" : item.color}`}>
                                                    {item.icon}
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <div className={`text-[12px] font-bold tracking-tight truncate ${isSelected ? "text-white" : "text-slate-700"}`}>{item.label}</div>
                                                    <div className={`text-[9px] font-medium truncate ${isSelected ? "text-white/80" : "text-slate-400"}`}>{item.sub}</div>
                                                </div>
                                                {isSelected && <ArrowRight size={14} className="text-white shrink-0" />}
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>

                            {/* Quick Actions Footer */}
                            <div className="bg-slate-50/80 p-5 border-t border-slate-100">
                                <div className="text-[8px] font-black text-slate-400 uppercase tracking-[0.15em] mb-3">Quick Actions</div>
                                <div className="grid grid-cols-2 gap-2.5">
                                    <button className="flex items-center justify-center gap-2 bg-white border border-slate-200 py-2.5 rounded-2xl shadow-sm hover:bg-slate-50 transition-all font-bold text-[10px] text-slate-600">
                                        <Settings size={12} className="text-slate-400" />
                                        Settings
                                    </button>
                                    <button className="flex items-center justify-center gap-2 bg-white border border-slate-200 py-2.5 rounded-2xl shadow-sm hover:bg-slate-50 transition-all font-bold text-[10px] text-slate-600">
                                        <Bell size={12} className="text-slate-400" />
                                        Notifications
                                    </button>
                                </div>
                            </div>
                        </div>
                    </>
                )}
            </div>

            {/* Notifications */}
            <div className="relative w-10 h-10 flex items-center justify-center border border-slate-200 rounded-2xl cursor-pointer hover:bg-slate-50 transition-all hover:border-slate-300 group">
                <Bell size={18} className="text-slate-500 group-hover:text-slate-900 transition-colors" />
                <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-orange-500 rounded-full border-2 border-white shadow-sm" />
            </div>

            {/* Settings */}
            <div className="w-10 h-10 flex items-center justify-center border border-slate-200 rounded-2xl cursor-pointer hover:bg-slate-50 transition-all hover:border-slate-300 group">
                <Settings size={18} className="text-slate-500 group-hover:text-slate-900 transition-colors" />
            </div>

            {/* Profile */}
            <button className="flex items-center gap-3 bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-2xl p-1.5 pr-4 shadow-lg shadow-orange-500/25 hover:shadow-orange-500/35 transition-all active:scale-95 group">
                <div className="w-9 h-9 bg-white/20 rounded-xl flex items-center justify-center font-bold text-sm backdrop-blur-sm group-hover:bg-white/30 transition-colors">{(user?.full_name || "S")[0]}</div>
                <div className="flex flex-col items-start leading-none">
                    <span className="text-sm font-bold tracking-tight">{user?.full_name?.split(' ')[0] || "Saif"}</span>
                    <span className="text-[10px] font-bold opacity-80 uppercase tracking-wider mt-0.5">{user?.role || "owner"}</span>
                </div>
                <ChevronDown size={14} className="ml-1 opacity-60" />
            </button>
        </header>
    );
}