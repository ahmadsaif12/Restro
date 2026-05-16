"use client";

import { usePathname, useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth-store";
import { authService } from "@/lib/api";
import Link from "next/link";
import { 
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
    Calendar,
    LogOut,
    UtensilsCrossed,
    CreditCard,
    Truck,
    Users
} from "lucide-react";

const navItems = [
    { icon: <LayoutDashboard size={20} />, label: "Dashboard", href: "/dashboard" },
    { icon: <TrendingUp size={20} />, label: "Executive Dashboard", href: "/dashboard/executive" },
    { icon: <Monitor size={20} />, label: "POS", href: "/dashboard/pos" },
    { icon: <ClipboardList size={20} />, label: "Orders", href: "/dashboard/orders" },
    { icon: <ChefHat size={20} />, label: "Kitchen", href: "/dashboard/kitchen" },
    { icon: <Pin size={20} />, label: "Prep Board", href: "/dashboard/prep" },
    { icon: <Utensils size={20} />, label: "Menu", href: "/dashboard/menu" },
    { icon: <QrCode size={20} />, label: "QR Menu", href: "/dashboard/qr-menu" },
    { icon: <Package size={20} />, label: "Inventory", href: "/dashboard/inventory" },
    { icon: <BookOpen size={20} />, label: "Recipes", href: "/dashboard/recipes" },
    { icon: <BarChart2 size={20} />, label: "Reports", href: "/dashboard/reports" },
    { icon: <Wallet size={20} />, label: "Expenses", href: "/dashboard/expenses" },
    { icon: <Calendar size={20} />, label: "Calendar", href: "/dashboard/calendar" },
    { icon: <CreditCard size={20} />, label: "Credit Management", href: "/dashboard/credit" },
    { icon: <Truck size={20} />, label: "Vendor Management", href: "/dashboard/vendors" },
    { icon: <Users size={20} />, label: "Staff Management", href: "/dashboard/staff" },
];

export default function Sidebar() {
    const pathname = usePathname();
    const router = useRouter();
    const { logout } = useAuthStore();

    const handleLogout = async () => {
        try {
            await authService.logout();
        } catch (err) {
            console.error("Logout error:", err);
        } finally {
            logout();
            router.push("/login");
        }
    };

    return (
        <aside className="fixed left-0 top-0 bottom-0 w-[300px] bg-[#0f172a] flex flex-col z-50 border-r border-slate-800">
            {/* Brand */}
            <div className="sticky top-0 bg-[#0f172a] z-10 flex items-center gap-3 px-6 py-10 border-b border-slate-800/50 shadow-sm">
                <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center shadow-xl shadow-orange-500/20 ring-4 ring-orange-500/10">
                    <UtensilsCrossed color="white" size={24} />
                </div>
                <div>
                    <div className="text-white font-black text-lg leading-tight tracking-tight">Handle My Restro</div>
                    <div className="text-slate-500 text-[10px] uppercase tracking-widest font-bold mt-0.5">Management System</div>
                </div>
            </div>

            {/* Nav */}
            <nav className="flex-1 px-4 py-2 space-y-1.5 overflow-y-auto custom-scrollbar">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.label}
                            href={item.href}
                            className={`flex items-center gap-3 px-4 py-3.5 rounded-2xl text-[13px] transition-all duration-300 group ${isActive
                                ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold shadow-[0_10px_20px_rgba(6,182,212,0.3)]"
                                : "text-slate-400 hover:text-white hover:bg-slate-800/50"
                                }`}
                        >
                            <span className={`${isActive ? "text-white" : "group-hover:text-cyan-400 transition-colors duration-300"}`}>
                                {item.icon}
                            </span>
                            <span className="flex-1 tracking-tight">{item.label}</span>
                        </Link>
                    );
                })}
            </nav>

            {/* Sign Out */}
            <div className="px-4 pb-10 pt-4 border-t border-slate-800 mt-4">
                <button 
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-4 py-3.5 rounded-2xl text-[13px] font-bold text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-all duration-300"
                >
                    <LogOut size={20} />
                    Sign Out
                </button>
            </div>
        </aside>
    );
}