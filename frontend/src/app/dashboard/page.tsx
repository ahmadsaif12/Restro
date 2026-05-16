import { fetchDashboardData } from "@/lib/api";
import Sidebar from "@/components/dashboard/Sidebar";
import Topbar from "@/components/dashboard/Topbar";
import StatCard from "@/components/dashboard/StatCard";
import PaymentCard from "@/components/dashboard/PaymentCard";
import RecentOrders from "@/components/dashboard/RecentOrders";
import { 
    Banknote, 
    ShoppingCart, 
    Clock, 
    CheckCircle2, 
    CreditCard, 
    Smartphone, 
    Receipt 
} from "lucide-react";

export default async function DashboardPage() {
    const data = await fetchDashboardData();

    return (
        <div className="flex min-h-screen">
            <Sidebar />
            <div className="ml-[300px] flex-1 flex flex-col">
                <Topbar />
                <main className="p-10 lg:p-12 flex-1 max-w-[1600px]">

                    {/* Business Overview */}
                    <div className="mb-10">
                        <h2 className="font-extrabold text-3xl text-gray-900 tracking-tight">Business Overview</h2>
                        <p className="text-sm text-gray-500 mt-2 font-medium">Real-time dashboard for today's performance</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
                        <StatCard
                            label="Today's Revenue"
                            value={`Rs ${data.stats.todayRevenue}`}
                            sub={`${data.stats.completedOrders} completed orders`}
                            icon={<Banknote size={28} />}
                            color="emerald"
                        />
                        <StatCard
                            label="Today's Orders"
                            value={String(data.stats.todayOrders)}
                            sub="Total orders placed today"
                            icon={<ShoppingCart size={28} />}
                            color="blue"
                        />
                        <StatCard
                            label="Pending Orders"
                            value={String(data.stats.pendingOrders)}
                            sub="Orders requiring attention"
                            icon={<Clock size={28} />}
                            color="orange"
                        />
                        <StatCard
                            label="Completed"
                            value={String(data.stats.completedOrders)}
                            sub="Successfully served"
                            icon={<CheckCircle2 size={28} />}
                            color="green"
                        />
                    </div>

                    {/* Payment Breakdown */}
                    <div className="mb-8">
                        <div className="flex items-center gap-2 mb-6">
                            <span className="p-2 bg-orange-100 text-orange-600 rounded-lg">
                                <Receipt size={18} />
                            </span>
                            <h3 className="font-bold text-xl text-gray-800 tracking-tight">Payment Methods Breakdown</h3>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
                            <PaymentCard 
                                label="Cash Payments" 
                                value={data.payments.cash} 
                                icon={<Banknote size={28} />} 
                                color="emerald" 
                                sub="Direct cash transactions" 
                            />
                            <PaymentCard 
                                label="Credit Card" 
                                value={data.payments.creditCard} 
                                icon={<CreditCard size={28} />} 
                                color="blue" 
                                sub="Card terminal payments" 
                            />
                            <PaymentCard 
                                label="Online Payment" 
                                value={data.payments.online} 
                                icon={<Smartphone size={28} />} 
                                color="purple" 
                                sub="Digital wallet / Fonepay" 
                            />
                            <PaymentCard 
                                label="Credit" 
                                value={data.payments.credit} 
                                icon={<Receipt size={28} />} 
                                color="orange" 
                                sub="Khata / Credit management" 
                            />
                        </div>
                    </div>

                    {/* Recent Orders */}
                    <RecentOrders orders={data.recentOrders} />

                </main>
            </div>
        </div>
    );
}