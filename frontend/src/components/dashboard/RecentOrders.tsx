import { Order } from "@/types/dashboard";
import { ArrowUpRight } from "lucide-react";

export default function RecentOrders({ orders }: { orders: Order[] }) {
    return (
        <div className="bg-white rounded-[32px] shadow-sm border border-slate-100 overflow-hidden">
            <div className="flex items-center justify-between px-8 py-6 border-b border-slate-50">
                <div>
                    <h3 className="font-bold text-lg text-slate-900 tracking-tight">Recent Orders</h3>
                    <p className="text-xs text-slate-400 font-medium mt-0.5">Summary of latest transactions</p>
                </div>
                <button className="flex items-center gap-2 text-xs font-bold text-blue-600 bg-blue-50 hover:bg-blue-100 px-4 py-2.5 rounded-2xl transition-colors">
                    View all orders
                    <ArrowUpRight size={14} />
                </button>
            </div>

            <div className="overflow-x-auto">
                {orders.length === 0 ? (
                    <div className="text-center text-slate-400 py-16 text-sm font-medium">
                        No orders recorded yet today
                    </div>
                ) : (
                    <div className="divide-y divide-slate-50">
                        {orders.map((order) => (
                            <div key={order.id} className="flex items-center gap-6 px-8 py-5 hover:bg-slate-50/50 transition-colors cursor-pointer group">
                                <div className="min-w-[120px]">
                                    <div className="font-bold text-sm text-slate-900 group-hover:text-blue-600 transition-colors">
                                        ORD-{order.id.split('-')[0].toUpperCase()}
                                    </div>
                                    <div className="flex items-center gap-2 mt-1">
                                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{order.table}</span>
                                        <span className="w-1 h-1 rounded-full bg-slate-300" />
                                        <span className="text-[10px] font-bold text-slate-300 uppercase tracking-wider">{order.time}</span>
                                    </div>
                                </div>
                                
                                <div className="flex gap-2">
                                    <span className={`text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-wider ${order.status === "PAID"
                                        ? "bg-emerald-50 text-emerald-600 border border-emerald-100"
                                        : "bg-orange-50 text-orange-500 border border-orange-100"
                                        }`}>
                                        {order.status}
                                    </span>
                                    <span className="text-[10px] font-bold px-3 py-1 rounded-full bg-slate-50 text-slate-500 border border-slate-100 uppercase tracking-wider">
                                        {order.paymentMethod}
                                    </span>
                                </div>

                                <div className="ml-auto text-right">
                                    <div className="font-bold text-emerald-600 text-base">Rs {order.amount.toLocaleString()}</div>
                                    <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mt-0.5">{order.items} items</div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}